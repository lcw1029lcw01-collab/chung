# -*- coding: utf-8 -*-
"""v0.2 수동 제작 루프 테스트.

규칙: 임시 루트만 사용, 외부 API 호출 없음, 실제 runtime 산출물 생성 없음.
tiny placeholder 파일은 임시 디렉터리 안에서만 만든다.
실행: 프로젝트 루트에서
  python -m unittest tests.test_manual_production_loop -v
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
    load_json,
    load_yaml,
    write_text,
)
from engines.assets import AssetRegistry  # noqa: E402
from engines.manual_production import (  # noqa: E402
    ManualIntakeManager,
    ManualProductionLoop,
    ManualWorkspaceManager,
)
from engines.manual_production.manual_workspace_manager import (  # noqa: E402
    ASSET_FOLDERS,
)
from engines.pipeline import FullPipelineRunner  # noqa: E402

DOCS_DIR = PROJECT_ROOT / "docs"
# docs/00~32 + MASTER_PLAN 불변 검증 (33은 v0.2 수동 루프 신규 문서라 제외)
_CORE_DOCS = sorted(
    p for p in DOCS_DIR.glob("*.md")
    if p.name == "MASTER_PLAN.md" or (p.name[:2].isdigit() and int(p.name[:2]) <= 32)
)
_DOCS_SNAPSHOT = [(p.name, p.stat().st_size, p.stat().st_mtime_ns) for p in _CORE_DOCS]
_RUNTIME_SNAPSHOT = {
    "channels": sorted(p.name for p in (PROJECT_ROOT / "channels").iterdir()),
    "projects": sorted(p.name for p in (PROJECT_ROOT / "projects").iterdir()),
}

SAMPLE_TEMPLATE_YAML = (
    PROJECT_ROOT / "templates" / "future_documentary_template" / "template.yaml"
)

PLACEHOLDER_TEXT = "TEST ONLY placeholder. Not real media.\n"


def make_temp_pm(tmp: Path) -> ADOSPathManager:
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    dst = tmp / "templates" / "future_documentary_template"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(SAMPLE_TEMPLATE_YAML, dst / "template.yaml")
    return ADOSPathManager(tmp)


class LoopBase(unittest.TestCase):
    """전체 파이프라인 + 업로드 준비 + 수동 루프 준비를 공유하는 베이스."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.tmp_root = Path(cls.tmp.name).resolve()
        cls.pm = make_temp_pm(cls.tmp_root)
        cls.runner = FullPipelineRunner(cls.pm)
        cls.summary = cls.runner.run_full_dummy_pipeline_with_upload_preparation()
        cls.project_path = Path(cls.summary["project_path"])
        cls.loop = ManualProductionLoop()
        cls.prep = cls.loop.prepare_manual_loop(cls.project_path)
        cls.project_id = cls.prep["project_id"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()


class TestManualProductionConfig(unittest.TestCase):
    def test_manual_production_yaml_safe_defaults(self):
        config = load_yaml(PROJECT_ROOT / "config" / "manual_production.yaml")
        self.assertEqual(config["manual_workspace_root"], "manual_assets")
        self.assertFalse(config["allow_file_copy"])
        self.assertFalse(config["allow_upload"])
        self.assertTrue(config["require_human_review"])
        self.assertTrue(config["require_real_final_video"])
        self.assertEqual(
            config["supported_asset_types"],
            ["image", "motion", "audio", "subtitle", "video", "thumbnail"],
        )

    def test_manual_assets_is_gitignored(self):
        gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("manual_assets/", gitignore)


class TestManualWorkspace(LoopBase):
    def test_workspace_created_under_manual_assets(self):
        workspaces = ManualWorkspaceManager()
        workspace = workspaces.workspace_path(self.project_path)
        self.assertEqual(
            workspace, self.tmp_root / "manual_assets" / self.project_id
        )
        self.assertTrue(workspace.is_dir())

    def test_workspace_folders_created(self):
        workspace = Path(self.prep["workspace_path"])
        for folder in ASSET_FOLDERS:
            self.assertTrue((workspace / folder).is_dir(), folder)
        self.assertTrue((workspace / "README.md").is_file())

    def test_workspace_info_safe_defaults(self):
        workspaces = ManualWorkspaceManager()
        info = workspaces.load_workspace_info(self.project_path)
        self.assertEqual(info["project_id"], self.project_id)
        self.assertFalse(info["allow_file_copy"])
        self.assertFalse(info["upload_ready"])
        self.assertIn("not automatically uploaded", info["disclaimer"])
        self.assertTrue(workspaces.validate_manual_workspace(self.project_path))


class TestIntakeManifest(LoopBase):
    def setUp(self):
        self.intake = ManualIntakeManager()

    def test_manifest_created_and_valid(self):
        manifest = self.intake.load_asset_intake_manifest(self.project_path)
        self.assertEqual(manifest["project_id"], self.project_id)
        self.assertEqual(manifest["intake_mode"], "manual")
        self.assertIn("assets/asset_requirements.json", manifest["sources"])
        self.assertTrue(
            self.intake.validate_asset_intake_manifest(self.project_path)
        )

    def test_items_based_on_asset_requirements(self):
        requirements = load_json(
            self.project_path / "assets" / "asset_requirements.json"
        )
        manifest = self.intake.load_asset_intake_manifest(self.project_path)
        counts = {}
        for item in manifest["items"]:
            counts[item["asset_type"]] = counts.get(item["asset_type"], 0) + 1
        for asset_type in requirements["required_asset_types"]:
            self.assertEqual(
                counts.get(asset_type, 0),
                requirements["expected_counts"][asset_type],
                asset_type,
            )
        for item in manifest["items"]:
            self.assertEqual(item["status"], "WAITING_FOR_HUMAN")
            self.assertIsNone(item["actual_file_path"])
            self.assertTrue(item["required"])
            self.assertTrue(
                item["expected_file_path"].startswith(
                    f"manual_assets/{self.project_id}/"
                )
            )

    def test_update_item_records_actual_file_path(self):
        manifest = self.intake.load_asset_intake_manifest(self.project_path)
        item_id = manifest["items"][0]["item_id"]
        updated = self.intake.update_asset_intake_item(
            self.project_path, item_id,
            file_path="C:/somewhere/file.png", notes="사람이 배치함",
        )
        self.assertEqual(updated["actual_file_path"], "C:/somewhere/file.png")
        self.assertEqual(updated["status"], "FILE_ASSIGNED")
        self.assertEqual(updated["notes"], "사람이 배치함")
        reloaded = self.intake.load_asset_intake_manifest(self.project_path)
        self.assertEqual(
            reloaded["items"][0]["actual_file_path"], "C:/somewhere/file.png"
        )

    def test_update_unknown_item_fails(self):
        with self.assertRaises(ADOSFileNotFoundError):
            self.intake.update_asset_intake_item(self.project_path, "MI999")


class TestImportReadyAssets(LoopBase):
    def test_import_records_metadata_only_and_links_registry(self):
        manifest = self.loop.intake.load_asset_intake_manifest(self.project_path)
        image_item = next(
            i for i in manifest["items"] if i["asset_type"] == "image"
        )
        video_item = next(
            i for i in manifest["items"] if i["asset_type"] == "video"
        )

        # tiny placeholder는 임시 디렉터리 안에서만 만든다
        source = self.tmp_root / "external_source" / "made_by_human.png"
        write_text(source, PLACEHOLDER_TEXT)
        self.loop.intake.update_asset_intake_item(
            self.project_path, image_item["item_id"], file_path=str(source)
        )
        self.loop.intake.update_asset_intake_item(
            self.project_path, video_item["item_id"],
            file_path="C:/nowhere/final_video.mp4",
        )

        registered = self.loop.import_ready_assets(self.project_path)
        self.assertEqual(registered, 2)

        # 파일 복사 없음 — expected 위치에 파일이 생기지 않는다
        expected_target = self.tmp_root / image_item["expected_file_path"]
        self.assertFalse(expected_target.exists())
        self.assertTrue(source.is_file())

        # AssetRegistry 연결 확인 (image는 ProviderImporter 경유)
        registry_manifest = AssetRegistry().load_production_asset_manifest(
            self.project_path
        )
        registered_paths = {a["file_path"] for a in registry_manifest["assets"]}
        self.assertIn(str(source), registered_paths)
        for asset in registry_manifest["assets"]:
            self.assertFalse(asset["copied"])
            self.assertFalse(asset["production_ready"])

        import_manifest = self.loop.importer.load_provider_import_manifest(
            self.project_path
        )
        self.assertEqual(len(import_manifest["imports"]), 1)
        self.assertEqual(import_manifest["imports"][0]["provider_name"], "midjourney")
        self.assertTrue(import_manifest["imports"][0]["linked_to_asset_registry"])

        # intake item 상태가 REGISTERED로 갱신되고 재실행 시 중복 등록되지 않는다
        reloaded = self.loop.intake.load_asset_intake_manifest(self.project_path)
        statuses = {
            i["item_id"]: i["status"] for i in reloaded["items"]
        }
        self.assertEqual(statuses[image_item["item_id"]], "REGISTERED")
        self.assertEqual(statuses[video_item["item_id"]], "REGISTERED")
        self.assertEqual(self.loop.import_ready_assets(self.project_path), 0)

    def test_missing_files_keep_upload_ready_false(self):
        upload_ready = self.loop.rerun_final_readiness(self.project_path)
        self.assertFalse(upload_ready)
        report = self.loop.final_gate.load_final_quality_report(self.project_path)
        self.assertEqual(report["final_decision"], "BLOCKED")
        self.assertIn("real_assets_missing", report["upload_blockers"])


class TestReviewApprovalAloneNotEnough(LoopBase):
    def test_approving_reviews_alone_keeps_upload_ready_false(self):
        summary = self.loop.approve_required_reviews(
            self.project_path, reviewer="human", notes="테스트 승인"
        )
        self.assertTrue(summary["all_required_approved"])

        upload_ready = self.loop.rerun_final_readiness(self.project_path)
        self.assertFalse(upload_ready)

        report = self.loop.final_gate.load_final_quality_report(self.project_path)
        self.assertEqual(report["final_decision"], "BLOCKED")
        self.assertNotIn("human_review_not_approved", report["upload_blockers"])
        self.assertIn("real_assets_missing", report["upload_blockers"])
        self.assertIn("real_final_video_missing", report["upload_blockers"])

    def test_zz_manual_loop_report_created(self):
        # 위 테스트에서 rerun까지 끝난 상태 — 보고서 생성 검증
        self.loop.rerun_final_readiness(self.project_path)
        report = self.loop.create_manual_loop_report(self.project_path)
        path = self.loop.loop_report_path(self.project_path)
        self.assertTrue(path.is_file())
        self.assertEqual(report["project_id"], self.project_id)
        self.assertFalse(report["upload_ready"])
        self.assertEqual(report["registered_asset_count"], 0)
        self.assertIn("No upload was performed", report["disclaimer"])
        for field in (
            "workspace_path", "intake_manifest_path", "human_review_status",
            "final_quality_decision", "blockers", "created_at",
        ):
            self.assertIn(field, report)


class TestUploadGatePassTestOnly(LoopBase):
    """테스트 전용 경로 — 임시 루트 안 placeholder로만 gate PASS를 증명한다."""

    def test_gate_passes_only_with_all_files_and_approvals(self):
        manifest = self.loop.intake.load_asset_intake_manifest(self.project_path)
        for item in manifest["items"]:
            placeholder = self.tmp_root / item["expected_file_path"]
            write_text(placeholder, PLACEHOLDER_TEXT)
            self.loop.intake.update_asset_intake_item(
                self.project_path, item["item_id"], file_path=str(placeholder)
            )
        registered = self.loop.import_ready_assets(self.project_path)
        self.assertEqual(registered, len(manifest["items"]))

        # 승인 전에는 여전히 BLOCKED
        self.assertFalse(self.loop.rerun_final_readiness(self.project_path))

        self.loop.approve_required_reviews(self.project_path)
        upload_ready = self.loop.rerun_final_readiness(self.project_path)
        self.assertTrue(upload_ready)

        report = self.loop.final_gate.load_final_quality_report(self.project_path)
        self.assertEqual(report["final_decision"], "PASS")
        self.assertEqual(report["upload_blockers"], [])

        # 업로드 준비 체크리스트가 재생성되고 gate 결과를 반영한다
        checklist = load_json(
            self.loop.preparer.checklist_path(self.project_path)
        )
        self.assertTrue(checklist["final_video_present"])
        self.assertTrue(checklist["upload_ready"])

        loop_report = self.loop.create_manual_loop_report(self.project_path)
        self.assertTrue(loop_report["upload_ready"])
        self.assertEqual(
            loop_report["registered_asset_count"], len(manifest["items"])
        )


class TestZRepoUntouched(unittest.TestCase):
    def test_core_docs_not_modified(self):
        current = [(p.name, p.stat().st_size, p.stat().st_mtime_ns) for p in _CORE_DOCS]
        self.assertEqual(current, _DOCS_SNAPSHOT)

    def test_no_new_runtime_outputs_in_real_repo(self):
        current = {
            "channels": sorted(p.name for p in (PROJECT_ROOT / "channels").iterdir()),
            "projects": sorted(p.name for p in (PROJECT_ROOT / "projects").iterdir()),
        }
        self.assertEqual(current, _RUNTIME_SNAPSHOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
