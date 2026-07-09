# -*- coding: utf-8 -*-
"""Asset Registry + Human Review + Final Quality Gate + Upload Preparation 테스트.

규칙: 임시 루트만 사용. 작은 더미 파일은 임시 폴더 안에서만 생성한다.
실행: 프로젝트 루트에서
  python -m unittest tests.test_asset_review_upload_preparation -v
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import (  # noqa: E402
    ADOSFileNotFoundError,
    ADOSPathManager,
    ADOSValidationError,
    load_json,
)
from engines.assets import AssetRegistry  # noqa: E402
from engines.final_quality import FinalQualityGate  # noqa: E402
from engines.pipeline import FullPipelineRunner  # noqa: E402
from engines.reporting import OperationReportGenerator  # noqa: E402
from engines.review import HumanReviewEngine  # noqa: E402
from engines.upload import UploadPreparer  # noqa: E402

DOCS_DIR = PROJECT_ROOT / "docs"
_DOCS_SNAPSHOT = sorted(
    (p.name, p.stat().st_size, p.stat().st_mtime_ns)
    for p in DOCS_DIR.rglob("*.md")
)
# 실제 저장소 runtime 폴더 불변 검증용 스냅샷
_RUNTIME_SNAPSHOT = {
    "channels": sorted(p.name for p in (PROJECT_ROOT / "channels").iterdir()),
    "projects": sorted(p.name for p in (PROJECT_ROOT / "projects").iterdir()),
}

SAMPLE_TEMPLATE_YAML = (
    PROJECT_ROOT / "templates" / "future_documentary_template" / "template.yaml"
)

ALL_CHECKPOINTS = [
    "STORY_REVIEW", "DIRECTION_REVIEW", "VISUAL_REVIEW",
    "EDITING_REVIEW", "QUALITY_REVIEW", "UPLOAD_REVIEW",
]


def make_temp_pm(tmp: Path) -> ADOSPathManager:
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    dst = tmp / "templates" / "future_documentary_template"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(SAMPLE_TEMPLATE_YAML, dst / "template.yaml")
    return ADOSPathManager(tmp)


class FullPrepBase(unittest.TestCase):
    """전체 파이프라인 + 업로드 준비를 한 번 완주한 상태를 공유하는 베이스."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.pm = make_temp_pm(Path(cls.tmp.name))
        cls.runner = FullPipelineRunner(cls.pm)
        cls.summary = cls.runner.run_full_dummy_pipeline_with_upload_preparation()
        cls.project_path = Path(cls.summary["project_path"])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()


class TestAssetRegistry(FullPrepBase):
    def test_requirements_created(self):
        registry = AssetRegistry()
        requirements = load_json(registry.requirements_path(self.project_path))
        self.assertEqual(
            sorted(requirements["required_asset_types"]),
            sorted(["image", "motion", "audio", "subtitle", "video", "thumbnail"]),
        )
        self.assertEqual(requirements["expected_counts"]["video"], 1)
        self.assertEqual(requirements["expected_counts"]["image"], 3)
        self.assertEqual(requirements["expected_counts"]["audio"], 5)

    def test_manifest_created_empty(self):
        registry = AssetRegistry()
        manifest = registry.load_production_asset_manifest(self.project_path)
        self.assertEqual(manifest["assets"], [])
        self.assertFalse(manifest["production_ready"])

    def test_readiness_detects_missing_assets(self):
        readiness = load_json(AssetRegistry().readiness_path(self.project_path))
        self.assertFalse(readiness["real_assets_present"])
        self.assertEqual(
            sorted(readiness["missing_asset_types"]),
            sorted(["image", "motion", "audio", "subtitle", "video", "thumbnail"]),
        )
        self.assertFalse(readiness["production_ready"])


class TestAssetRegistration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_pm(Path(self.tmp.name))
        project = FullPipelineRunner(self.pm).create_sample_project()
        self.project_path = Path(project["path"])
        self.registry = AssetRegistry()
        self.registry.create_asset_requirements(self.project_path)
        self.registry.create_production_asset_manifest(self.project_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_register_metadata_without_copy(self):
        # 존재하지 않는 placeholder 경로
        item = self.registry.register_asset(
            self.project_path, "image", "C:/nowhere/img.png", "img.png"
        )
        self.assertEqual(item["asset_id"], "PA001")
        self.assertFalse(item["exists"])
        self.assertFalse(item["copied"])
        # 임시 폴더 안의 진짜 작은 더미 파일
        real_file = Path(self.tmp.name) / "tiny.mp4"
        real_file.write_bytes(b"dummy")
        item2 = self.registry.register_asset(
            self.project_path, "video", str(real_file), "final.mp4"
        )
        self.assertTrue(item2["exists"])
        self.assertFalse(item2["copied"])
        # 프로젝트 폴더로 복사되지 않았는지 확인
        self.assertFalse((self.project_path / "assets" / "final.mp4").exists())
        self.assertTrue(
            self.registry.validate_production_asset_manifest(self.project_path)
        )

    def test_unsupported_asset_type_fails(self):
        with self.assertRaises(ADOSValidationError):
            self.registry.register_asset(
                self.project_path, "hologram", "C:/x.png", "x.png"
            )


class TestHumanReview(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_pm(Path(self.tmp.name))
        project = FullPipelineRunner(self.pm).create_sample_project()
        self.project_path = Path(project["path"])
        self.engine = HumanReviewEngine()
        self.engine.create_review_checkpoints(self.project_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_checkpoints_created(self):
        data = load_json(self.engine.checkpoints_path(self.project_path))
        self.assertEqual(
            [c["checkpoint_id"] for c in data["checkpoints"]], ALL_CHECKPOINTS
        )
        self.assertTrue(all(c["status"] == "PENDING" for c in data["checkpoints"]))
        summary = self.engine.load_review_summary(self.project_path)
        self.assertEqual(summary["pending_count"], 6)
        self.assertFalse(summary["upload_allowed_by_human_review"])

    def test_approve_and_reject_update_summary(self):
        summary = self.engine.approve_checkpoint(
            self.project_path, "STORY_REVIEW", reviewer="이충원", notes="좋음"
        )
        self.assertEqual(summary["approved_count"], 1)
        summary = self.engine.reject_checkpoint(
            self.project_path, "VISUAL_REVIEW", notes="재작업 필요"
        )
        self.assertEqual(summary["rejected_count"], 1)
        self.assertEqual(summary["pending_count"], 4)
        self.assertFalse(summary["all_required_approved"])
        self.assertTrue(self.engine.validate_review_summary(self.project_path))
        with self.assertRaises(ADOSValidationError):
            self.engine.approve_checkpoint(self.project_path, "NO_SUCH_CHECKPOINT")


class TestFinalQualityGate(FullPrepBase):
    def test_blocked_in_normal_dummy_pipeline(self):
        """실자산 없음 + 검토 미승인 → BLOCKED가 정상."""
        gate = FinalQualityGate()
        report = gate.load_final_quality_report(self.project_path)
        self.assertEqual(report["final_decision"], "BLOCKED")
        self.assertFalse(report["upload_ready"])
        self.assertIn("real_assets_missing", report["upload_blockers"])
        self.assertIn("human_review_not_approved", report["upload_blockers"])
        self.assertIn("real_final_video_missing", report["upload_blockers"])
        self.assertTrue(gate.validate_final_quality_report(self.project_path))


class TestFinalGatePassPath(unittest.TestCase):
    """모든 조건 충족 시에만 PASS가 되는지 — 임시 더미 파일 + 전체 승인."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_pm(Path(self.tmp.name))
        runner = FullPipelineRunner(self.pm)
        summary = runner.run_full_dummy_pipeline_with_upload_preparation()
        self.project_path = Path(summary["project_path"])
        self.registry = AssetRegistry()
        self.review = HumanReviewEngine()
        self.gate = FinalQualityGate()

    def tearDown(self):
        self.tmp.cleanup()

    def _register_all_asset_types(self):
        for asset_type in ("image", "motion", "audio", "subtitle", "video", "thumbnail"):
            dummy = Path(self.tmp.name) / f"dummy_{asset_type}.bin"
            dummy.write_bytes(b"dummy")
            self.registry.register_asset(
                self.project_path, asset_type, str(dummy), f"{asset_type}.bin"
            )
        self.registry.create_asset_readiness_report(self.project_path)

    def test_blocked_when_only_assets_ready_but_review_pending(self):
        self._register_all_asset_types()
        report = self.gate.create_final_quality_report(self.project_path)
        self.assertEqual(report["final_decision"], "BLOCKED")
        self.assertEqual(report["upload_blockers"], ["human_review_not_approved"])

    def test_pass_when_all_conditions_satisfied(self):
        self._register_all_asset_types()
        for checkpoint in ALL_CHECKPOINTS:
            self.review.approve_checkpoint(self.project_path, checkpoint)
        report = self.gate.create_final_quality_report(self.project_path)
        self.assertEqual(report["final_decision"], "PASS")
        self.assertTrue(report["upload_ready"])
        self.assertEqual(report["upload_blockers"], [])
        # 게이트 통과 후 메타데이터 패키지도 upload_ready true를 반영
        package = UploadPreparer().create_youtube_metadata_package(self.project_path)
        self.assertTrue(package["upload_ready"])
        self.assertFalse(package["blocked_by_final_gate"])


class TestUploadPreparation(FullPrepBase):
    def test_youtube_metadata_package(self):
        preparer = UploadPreparer()
        package = load_json(preparer.metadata_path(self.project_path))
        self.assertEqual(package["platform"], "youtube")
        self.assertEqual(package["upload_mode"], "manual_preparation")
        self.assertEqual(package["default_language"], "ko")
        self.assertFalse(package["upload_ready"])
        self.assertTrue(package["blocked_by_final_gate"])

    def test_upload_readiness_checklist(self):
        checklist = load_json(UploadPreparer().checklist_path(self.project_path))
        self.assertFalse(checklist["upload_ready"])
        self.assertFalse(checklist["final_video_present"])
        self.assertFalse(checklist["human_review_approved"])
        self.assertFalse(checklist["final_quality_passed"])
        self.assertTrue(checklist["metadata_present"])

    def test_manual_upload_instructions(self):
        instructions = load_json(UploadPreparer().instructions_path(self.project_path))
        self.assertEqual(
            instructions["warning"],
            "Manual upload only. This system did not upload any video.",
        )
        self.assertGreaterEqual(len(instructions["steps"]), 5)
        self.assertTrue(UploadPreparer().validate_upload_package(self.project_path))

    def test_operation_report(self):
        generator = OperationReportGenerator()
        report = generator.load_operation_report(self.project_path)
        self.assertEqual(report["operation_mode"], "dummy_to_manual_handoff")
        self.assertEqual(report["workflow_status"], "COMPLETED")
        self.assertFalse(report["upload_ready"])
        self.assertFalse(report["real_assets_present"])
        self.assertEqual(report["final_quality_decision"], "BLOCKED")
        self.assertGreater(len(report["next_manual_actions"]), 0)
        self.assertTrue(generator.validate_operation_report(self.project_path))
        folder = self.project_path / "reports"
        for name in ("operation_report.json", "upload_preparation_report.json", "handoff_report.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")

    def test_runner_returns_upload_ready_false(self):
        self.assertFalse(self.summary["upload_preparation"]["upload_ready"])
        self.assertEqual(
            self.summary["upload_preparation"]["final_decision"], "BLOCKED"
        )


class TestZRepoUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        current = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(current, _DOCS_SNAPSHOT)

    def test_no_new_runtime_outputs_in_real_repo(self):
        current = {
            "channels": sorted(p.name for p in (PROJECT_ROOT / "channels").iterdir()),
            "projects": sorted(p.name for p in (PROJECT_ROOT / "projects").iterdir()),
        }
        self.assertEqual(current, _RUNTIME_SNAPSHOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
