# -*- coding: utf-8 -*-
"""v0.3 실제 수동 트라이얼 준비 테스트.

규칙: 임시 루트만 사용, 외부 API 호출 없음, 실제 runtime 산출물 생성 없음.
tiny temp 파일은 임시 디렉터리 안에서만 만든다.
실행: 프로젝트 루트에서
  python -m unittest tests.test_real_manual_trial_preparation -v
"""
import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from core import (  # noqa: E402
    ADOSPathManager,
    load_json,
    load_yaml,
    write_text,
)
from engines.asset_validation import (  # noqa: E402
    AssetFileValidator,
    RealAssetReadiness,
)
from engines.manual_trial import ManualTrialGuide, ManualTrialRunner  # noqa: E402
import run_real_manual_trial_finalize as finalize_script  # noqa: E402
import run_real_manual_trial_validate as validate_script  # noqa: E402

DOCS_DIR = PROJECT_ROOT / "docs"
# docs/00~33 + MASTER_PLAN 불변 검증 (34는 v0.3 신규 문서라 제외)
_CORE_DOCS = sorted(
    p for p in DOCS_DIR.glob("*.md")
    if p.name == "MASTER_PLAN.md" or (p.name[:2].isdigit() and int(p.name[:2]) <= 33)
)
_DOCS_SNAPSHOT = [(p.name, p.stat().st_size, p.stat().st_mtime_ns) for p in _CORE_DOCS]
_RUNTIME_SNAPSHOT = {
    "channels": sorted(p.name for p in (PROJECT_ROOT / "channels").iterdir()),
    "projects": sorted(p.name for p in (PROJECT_ROOT / "projects").iterdir()),
}

SAMPLE_TEMPLATE_YAML = (
    PROJECT_ROOT / "templates" / "future_documentary_template" / "template.yaml"
)


def make_temp_pm(tmp: Path) -> ADOSPathManager:
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    dst = tmp / "templates" / "future_documentary_template"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(SAMPLE_TEMPLATE_YAML, dst / "template.yaml")
    return ADOSPathManager(tmp)


class TrialBase(unittest.TestCase):
    """전체 파이프라인 + 트라이얼 준비를 한 번 완주한 상태를 공유하는 베이스."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.tmp_root = Path(cls.tmp.name).resolve()
        cls.pm = make_temp_pm(cls.tmp_root)
        cls.runner = ManualTrialRunner(cls.pm)
        cls.prep = cls.runner.prepare_real_manual_trial()
        cls.project_path = Path(cls.prep["project_path"])
        cls.project_id = cls.prep["project_id"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()


class TestAssetValidationConfig(unittest.TestCase):
    def test_asset_validation_yaml_safe_defaults(self):
        config = load_yaml(PROJECT_ROOT / "config" / "asset_validation.yaml")
        self.assertFalse(config["allow_upload"])
        self.assertFalse(config["allow_external_calls"])
        for asset_type in ("image", "motion", "audio", "video", "thumbnail"):
            self.assertEqual(config["minimum_file_sizes"][asset_type], 1024)
        self.assertEqual(config["minimum_file_sizes"]["subtitle"], 1)
        self.assertIn(".png", config["allowed_extensions"]["image"])
        self.assertIn(".mp4", config["allowed_extensions"]["video"])
        self.assertIn(".srt", config["allowed_extensions"]["subtitle"])

    def test_manual_assets_still_gitignored(self):
        gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("manual_assets/", gitignore)


class TestAssetFileValidator(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.validator = AssetFileValidator()

    def tearDown(self):
        self.tmp.cleanup()

    def test_valid_file_passes(self):
        path = self.tmp_path / "SC001.png"
        write_text(path, "x" * 2048)
        result = self.validator.validate_file(path, "image")
        self.assertTrue(result["exists"])
        self.assertTrue(result["extension_allowed"])
        self.assertTrue(result["size_ok"])
        self.assertEqual(result["validation_status"], "PASS")
        self.assertEqual(result["issues"], [])

    def test_wrong_extension_fails(self):
        path = self.tmp_path / "SC001.txt"
        write_text(path, "x" * 2048)
        result = self.validator.validate_file(path, "image")
        self.assertFalse(result["extension_allowed"])
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("extension_not_allowed" in i for i in result["issues"]))

    def test_too_small_file_fails(self):
        path = self.tmp_path / "SC001.png"
        write_text(path, "x" * 10)
        result = self.validator.validate_file(path, "image")
        self.assertTrue(result["exists"])
        self.assertFalse(result["size_ok"])
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertTrue(any("file_too_small" in i for i in result["issues"]))

    def test_missing_file_fails(self):
        result = self.validator.validate_file(
            self.tmp_path / "nowhere.png", "image"
        )
        self.assertFalse(result["exists"])
        self.assertEqual(result["validation_status"], "FAIL")
        self.assertIn("file_missing", result["issues"])


class TestPrepareTrial(TrialBase):
    def test_prepare_keeps_upload_ready_false(self):
        self.assertFalse(self.prep["upload_ready"])
        self.assertTrue(self.prep["next_human_action"])

    def test_guide_files_created(self):
        guide = ManualTrialGuide()
        self.assertTrue(guide.guide_path(self.project_path).is_file())
        self.assertTrue(guide.checklist_path(self.project_path).is_file())
        self.assertTrue(guide.guide_md_path(self.project_path).is_file())
        self.assertTrue(guide.validate_trial_guide(self.project_path))
        md = guide.guide_md_path(self.project_path).read_text(encoding="utf-8")
        self.assertIn("REAL MANUAL TRIAL GUIDE", md)
        self.assertIn("video/final_video.mp4", md)
        # 마크다운 가이드에도 단일 진실(source of truth) 안내가 포함된다
        self.assertIn("source of truth", md)

    def test_guide_expected_files_match_intake_manifest(self):
        guide = ManualTrialGuide().load_trial_guide(self.project_path)
        files = [e["file"] for e in guide["expected_asset_files"]]
        # intake manifest의 expected_file_path와 정확히 일치해야 한다 (단일 진실)
        intake = self.runner.loop.intake.load_asset_intake_manifest(
            self.project_path
        )
        prefix = f"manual_assets/{self.project_id}/"
        expected = [
            i["expected_file_path"][len(prefix):] for i in intake["items"]
        ]
        self.assertEqual(files, expected)
        self.assertIn("source of truth", guide["source_of_truth_note"])
        # export pack 3종이 가이드에 연결된다
        self.assertEqual(len(guide["provider_export_pack_paths"]), 3)
        # 체크리스트는 기대 파일 + 검증/검토/최종화 단계를 포함한다
        checklist = load_json(
            ManualTrialGuide().checklist_path(self.project_path)
        )
        self.assertEqual(len(checklist["items"]), len(files) + 3)

    def test_guide_fallback_without_intake_manifest(self):
        intake_path = self.runner.loop.intake.manifest_path(self.project_path)
        backup = intake_path.with_name("asset_intake_manifest.json.bak")
        intake_path.rename(backup)
        try:
            guide = ManualTrialGuide().create_trial_guide(self.project_path)
            files = [e["file"] for e in guide["expected_asset_files"]]
            # intake manifest가 없으면 plan 기반 결정적 fallback 이름을 쓴다
            self.assertIn("images/SC001.png", files)
            self.assertIn("motion/SC001.mp4", files)
            self.assertIn("audio/voice_ko.mp3", files)
            self.assertIn("video/final_video.mp4", files)
            self.assertIn("thumbnail/thumbnail.jpg", files)
            self.assertIn("source of truth", guide["source_of_truth_note"])
        finally:
            backup.rename(intake_path)
            # 공유 상태 원복 — intake 기반 가이드 재생성
            ManualTrialGuide().create_trial_guide(self.project_path)


class TestValidateWithoutFiles(TrialBase):
    def test_validate_remains_false_without_files(self):
        summary = self.runner.validate_real_manual_trial(self.project_path)
        self.assertFalse(summary["upload_ready"])
        self.assertFalse(summary["real_assets_present"])
        self.assertFalse(summary["production_ready_candidate"])
        self.assertEqual(summary["registered_this_run"], 0)
        self.assertIn("real_assets_missing", summary["blockers"])
        readiness = RealAssetReadiness().load_real_asset_readiness_report(
            self.project_path
        )
        self.assertTrue(readiness["missing_asset_types"])
        self.assertTrue(
            RealAssetReadiness().validate_real_asset_readiness_report(
                self.project_path
            )
        )


class TestValidateWithValidTempFiles(TrialBase):
    """임시 루트 안에서만 유효한 tiny 파일로 전체 흐름을 검증한다."""

    def test_full_trial_flow_with_valid_temp_files(self):
        intake = self.runner.loop.intake
        manifest = intake.load_asset_intake_manifest(self.project_path)
        for item in manifest["items"]:
            placed = self.tmp_root / item["expected_file_path"]
            write_text(placed, "x" * 2048)  # 최소 크기(1024) 이상, 허용 확장자
            intake.update_asset_intake_item(
                self.project_path, item["item_id"], file_path=str(placed)
            )

        summary = self.runner.validate_real_manual_trial(self.project_path)
        self.assertEqual(summary["registered_this_run"], len(manifest["items"]))
        self.assertEqual(summary["validation_fail_count"], 0)
        self.assertEqual(
            summary["validation_pass_count"], len(manifest["items"])
        )
        self.assertTrue(summary["real_assets_present"])
        self.assertTrue(summary["real_final_video_present"])
        self.assertTrue(summary["production_ready_candidate"])
        # 검토 미승인 → 여전히 false
        self.assertFalse(summary["upload_ready"])
        self.assertIn("human_review_not_approved", summary["blockers"])

        # 명시적 승인 후 finalize → 게이트가 실제로 통과해야만 true
        self.runner.approve_real_manual_trial_reviews(
            self.project_path, notes="임시 파일 기반 트라이얼 테스트"
        )
        upload_ready = self.runner.finalize_real_manual_trial(self.project_path)
        self.assertTrue(upload_ready)

        # finalize는 업로드하지 않는다 — 패키지·안내 문서만 생성
        preparer = self.runner.loop.preparer
        package = load_json(preparer.metadata_path(self.project_path))
        self.assertIn("No upload was performed", package["disclaimer"])
        instructions = load_json(preparer.instructions_path(self.project_path))
        self.assertIn("did not upload", instructions["warning"])


class TestValidatorReportOnRegisteredAssets(TrialBase):
    def test_registered_asset_validation_report(self):
        intake = self.runner.loop.intake
        manifest = intake.load_asset_intake_manifest(self.project_path)
        image_item = next(
            i for i in manifest["items"] if i["asset_type"] == "image"
        )
        # 확장자는 맞지만 너무 작은 파일 → FAIL로 기록된다
        placed = self.tmp_root / image_item["expected_file_path"]
        write_text(placed, "tiny")
        intake.update_asset_intake_item(
            self.project_path, image_item["item_id"], file_path=str(placed)
        )
        self.runner.loop.import_ready_assets(self.project_path)

        report = AssetFileValidator().validate_registered_assets(self.project_path)
        self.assertEqual(report["pass_count"], 0)
        self.assertEqual(report["fail_count"], 1)
        item = report["items"][0]
        self.assertTrue(item["asset_id"].startswith("PA"))
        self.assertFalse(item["size_ok"])
        self.assertEqual(item["validation_status"], "FAIL")
        self.assertIn("does not verify media content", report["disclaimer"])

        readiness = RealAssetReadiness().create_real_asset_readiness_report(
            self.project_path
        )
        self.assertFalse(readiness["real_assets_present"])
        self.assertEqual(len(readiness["invalid_assets"]), 1)


class TestScriptsUsage(unittest.TestCase):
    def _run_main(self, main, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = main(argv)
        return rc, out.getvalue()

    def test_validate_without_args_prints_usage(self):
        rc, output = self._run_main(validate_script.main, [])
        self.assertEqual(rc, 1)
        self.assertIn("사용법", output)

    def test_finalize_without_args_prints_usage(self):
        rc, output = self._run_main(finalize_script.main, [])
        self.assertEqual(rc, 1)
        self.assertIn("사용법", output)

    def test_invalid_project_path_prints_usage(self):
        for main in (validate_script.main, finalize_script.main):
            rc, output = self._run_main(main, ["C:/nowhere/not-a-project"])
            self.assertEqual(rc, 1)
            self.assertIn("사용법", output)


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
