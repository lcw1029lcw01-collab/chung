# -*- coding: utf-8 -*-
"""v0.2 Provider 통합 준비 테스트.

규칙: 임시 루트만 사용, 외부 API 호출 없음, 실제 runtime 산출물 생성 없음.
실행: 프로젝트 루트에서
  python -m unittest tests.test_provider_integration_prep -v
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
    load_yaml,
)
from engines.assets import AssetRegistry  # noqa: E402
from engines.final_quality import FinalQualityGate  # noqa: E402
from engines.pipeline import FullPipelineRunner  # noqa: E402
from engines.provider_jobs import (  # noqa: E402
    ProviderExporter,
    ProviderImporter,
    ProviderJobManager,
)
from providers import (  # noqa: E402
    MidjourneyProvider,
    MidjourneyVideoProvider,
    TypecastProvider,
)

DOCS_DIR = PROJECT_ROOT / "docs"
# docs/00~31 + MASTER_PLAN 불변 검증 (32는 v0.2 신규 문서라 제외)
_CORE_DOCS = sorted(
    p for p in DOCS_DIR.glob("*.md")
    if p.name == "MASTER_PLAN.md" or (p.name[:2].isdigit() and int(p.name[:2]) <= 31)
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


class PrepBase(unittest.TestCase):
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


class TestProviderModesConfig(unittest.TestCase):
    def test_provider_modes_yaml_safe_defaults(self):
        config = load_yaml(PROJECT_ROOT / "config" / "provider_modes.yaml")
        self.assertEqual(config["default_mode"], "manual")
        self.assertFalse(config["allow_external_calls"])
        self.assertFalse(config["allow_uploads"])
        for name in ("midjourney", "midjourney_video", "typecast"):
            provider = config["providers"][name]
            self.assertTrue(provider["enabled"])
            self.assertEqual(provider["mode"], "manual")
            self.assertFalse(provider["external_calls_allowed"])


class TestProviderJobManager(PrepBase):
    def setUp(self):
        self.jobs = ProviderJobManager()
        self.jobs.create_job_queue(self.project_path)

    def test_queue_created(self):
        queue = self.jobs.load_job_queue(self.project_path)
        self.assertEqual(queue["jobs"], [])
        self.assertEqual(queue["queue_mode"], "manual")

    def test_create_jobs_for_all_providers(self):
        for provider in ("midjourney", "midjourney_video", "typecast"):
            job = self.jobs.create_provider_job(
                self.project_path, provider, "generation", "some/ref.json", {"k": 1}
            )
            self.assertEqual(job["status"], "CREATED")
            self.assertFalse(job["external_call_made"])
            self.assertTrue(
                self.jobs.job_path(self.project_path, job["job_id"]).is_file()
            )
        self.assertTrue(self.jobs.validate_job_queue(self.project_path))

    def test_invalid_provider_fails(self):
        with self.assertRaises(ADOSValidationError):
            self.jobs.create_provider_job(
                self.project_path, "dalle", "generation", "x", {}
            )

    def test_update_job_status(self):
        job = self.jobs.create_provider_job(
            self.project_path, "midjourney", "image_generation", "ref", {}
        )
        updated = self.jobs.update_job_status(
            self.project_path, job["job_id"], "EXPORTED", notes="pack 생성됨"
        )
        self.assertEqual(updated["status"], "EXPORTED")
        self.assertEqual(updated["notes"], "pack 생성됨")
        self.assertFalse(updated["external_call_made"])
        with self.assertRaises(ADOSValidationError):
            self.jobs.update_job_status(self.project_path, job["job_id"], "FLYING")
        with self.assertRaises(ADOSFileNotFoundError):
            self.jobs.update_job_status(self.project_path, "PJ999-x", "COMPLETED")


class TestProviderExporter(PrepBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.exporter = ProviderExporter()
        cls.exp_summary = cls.exporter.export_all_provider_packs(cls.project_path)

    def test_midjourney_pack(self):
        pack = load_json(
            self.exporter.exports_dir(self.project_path) / "midjourney_prompt_pack.json"
        )
        self.assertEqual(pack["provider_name"], "midjourney")
        self.assertEqual(pack["export_mode"], "manual")
        self.assertFalse(pack["external_call_made"])
        self.assertEqual(len(pack["items"]), 3)  # 3 scenes
        self.assertTrue(pack["instructions"])

    def test_midjourney_video_pack(self):
        pack = load_json(
            self.exporter.exports_dir(self.project_path)
            / "midjourney_video_prompt_pack.json"
        )
        self.assertEqual(pack["provider_name"], "midjourney_video")
        self.assertFalse(pack["external_call_made"])
        self.assertEqual(len(pack["items"]), 1)  # hook scene만 motion

    def test_typecast_pack(self):
        pack = load_json(
            self.exporter.exports_dir(self.project_path) / "typecast_script_pack.json"
        )
        self.assertEqual(pack["provider_name"], "typecast")
        self.assertFalse(pack["external_call_made"])
        self.assertEqual(len(pack["items"]), 5)  # 5 narration blocks

    def test_export_summary(self):
        self.assertEqual(
            self.exp_summary["item_counts"],
            {"midjourney": 3, "midjourney_video": 1, "typecast": 5},
        )
        self.assertFalse(self.exp_summary["external_call_made"])
        self.assertTrue(
            (self.exporter.exports_dir(self.project_path)
             / "provider_export_summary.json").is_file()
        )


class TestProviderImporter(PrepBase):
    def setUp(self):
        self.importer = ProviderImporter()

    def test_import_and_link(self):
        item = self.importer.import_provider_asset_metadata(
            self.project_path, "midjourney", "image",
            "C:/nowhere/SC001.png", "SC001.png",
            job_id="PJ001-midjourney", metadata={"scene_id": "SC001"},
        )
        self.assertEqual(item["import_id"], "PI001")
        self.assertFalse(item["exists"])
        self.assertFalse(item["linked_to_asset_registry"])
        manifest = self.importer.load_provider_import_manifest(self.project_path)
        self.assertEqual(len(manifest["imports"]), 1)
        self.assertTrue(
            self.importer.validate_provider_import_manifest(self.project_path)
        )
        # registry 연결
        linked = self.importer.link_import_to_asset_registry(
            self.project_path, "PI001"
        )
        self.assertTrue(linked["linked_to_asset_registry"])
        self.assertIsNotNone(linked["asset_registry_id"])
        registry_manifest = AssetRegistry().load_production_asset_manifest(
            self.project_path
        )
        registered = [
            a for a in registry_manifest["assets"]
            if a["asset_id"] == linked["asset_registry_id"]
        ]
        self.assertEqual(len(registered), 1)
        self.assertFalse(registered[0]["copied"])
        self.assertFalse(registered[0]["production_ready"])
        self.assertEqual(registered[0]["metadata"]["provider_name"], "midjourney")

    def test_invalid_provider_fails(self):
        with self.assertRaises(ADOSValidationError):
            self.importer.import_provider_asset_metadata(
                self.project_path, "dalle", "image", "x.png", "x.png"
            )

    def test_upload_ready_remains_false_after_imports(self):
        for provider, asset_type in (
            ("midjourney", "image"), ("midjourney_video", "motion"), ("typecast", "audio"),
        ):
            item = self.importer.import_provider_asset_metadata(
                self.project_path, provider, asset_type,
                f"C:/nowhere/{asset_type}.bin", f"{asset_type}.bin",
            )
            self.importer.link_import_to_asset_registry(
                self.project_path, item["import_id"]
            )
        AssetRegistry().create_asset_readiness_report(self.project_path)
        report = FinalQualityGate().create_final_quality_report(self.project_path)
        self.assertEqual(report["final_decision"], "BLOCKED")
        self.assertFalse(report["upload_ready"])


class TestPlaceholderProviders(unittest.TestCase):
    def test_placeholders_still_safe_and_support_manual(self):
        for provider in (MidjourneyProvider(), MidjourneyVideoProvider(), TypecastProvider()):
            job = provider.create_job({"dummy": True})
            self.assertEqual(job["status"], "NOT_SUBMITTED")
            self.assertFalse(job["external_call_made"])
            self.assertTrue(provider.supports_manual_mode())
            instructions = provider.get_manual_instructions()
            self.assertEqual(instructions["mode"], "manual")
            self.assertFalse(instructions["external_call_made"])
            self.assertGreaterEqual(len(instructions["instructions"]), 3)


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
