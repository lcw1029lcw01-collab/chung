# -*- coding: utf-8 -*-
"""AI Evolution + Growth + FullPipelineRunner + RunReport + Providers 테스트.

규칙: 임시 루트만 사용, 실제 channels/·projects/에 산출물을 만들지 않는다.
실행: 프로젝트 루트에서
  python -m unittest tests.test_ai_evolution_growth_pipeline_providers -v
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
    StageName,
    load_json,
)
from engines.ai_evolution import AIEvolutionEngine  # noqa: E402
from engines.growth import GrowthEngine  # noqa: E402
from engines.pipeline import FullPipelineRunner  # noqa: E402
from engines.reporting import RunReportGenerator  # noqa: E402
from providers import (  # noqa: E402
    ManualAssetImporter,
    MidjourneyProvider,
    MidjourneyVideoProvider,
    TypecastProvider,
)

DOCS_DIR = PROJECT_ROOT / "docs"
_DOCS_SNAPSHOT = sorted(
    (p.name, p.stat().st_size, p.stat().st_mtime_ns)
    for p in DOCS_DIR.rglob("*.md")
)

SAMPLE_TEMPLATE_YAML = (
    PROJECT_ROOT / "templates" / "future_documentary_template" / "template.yaml"
)

# 실제 워크플로우 stage 결과가 있어야 하는 18개 단계
REAL_STAGES = [
    "RESEARCH", "KNOWLEDGE", "STORY", "DIRECTION", "TIMELINE", "VISUAL",
    "MOTION", "VOICE", "SUBTITLE", "EDITING", "QUALITY", "AUTO_FIX",
    "PACKAGE", "READY", "PUBLISHED", "ANALYTICS", "LEARNING", "AI_EVOLUTION",
]


def make_temp_pm(tmp: Path) -> ADOSPathManager:
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    dst = tmp / "templates" / "future_documentary_template"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(SAMPLE_TEMPLATE_YAML, dst / "template.yaml")
    return ADOSPathManager(tmp)


class FullRunBase(unittest.TestCase):
    """전체 파이프라인을 한 번 완주시킨 상태를 공유하는 베이스."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.pm = make_temp_pm(Path(cls.tmp.name))
        cls.runner = FullPipelineRunner(cls.pm)
        cls.summary = cls.runner.run_full_dummy_pipeline()
        cls.project_path = Path(cls.summary["project_path"])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()


class TestRequirements(unittest.TestCase):
    """빈 프로젝트에서 사전 조건 검증."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_pm(Path(self.tmp.name))
        project = FullPipelineRunner(self.pm).create_sample_project()
        self.project_path = Path(project["path"])

    def tearDown(self):
        self.tmp.cleanup()

    def test_ai_evolution_requires_learning_outputs(self):
        with self.assertRaises(ADOSFileNotFoundError):
            AIEvolutionEngine().create_dummy_ai_evolution_report(self.project_path)

    def test_growth_requires_analytics_and_publishing(self):
        with self.assertRaises(ADOSFileNotFoundError):
            GrowthEngine().create_dummy_growth_report(self.project_path)


class TestFullPipelineRun(FullRunBase):
    def test_pipeline_reaches_complete_after_ai_evolution(self):
        self.assertEqual(self.summary["final_stage"], "COMPLETE")
        self.assertEqual(self.summary["workflow_status"], "COMPLETED")
        self.assertEqual(self.summary["completed_stages"], REAL_STAGES)

    def test_stage_results_exist_for_all_real_stages(self):
        results_dir = self.project_path / "workflow" / "stage_results"
        for stage in REAL_STAGES:
            self.assertTrue(
                (results_dir / f"{stage}_result.json").is_file(),
                f"stage result 누락: {stage}",
            )

    def test_growth_is_advisory_not_a_stage(self):
        # Growth 산출물과 advisory result 파일은 존재
        self.assertTrue(
            (self.project_path / "analytics" / "growth_report.json").is_file()
        )
        growth_result = load_json(
            self.project_path / "workflow" / "stage_results" / "GROWTH_result.json"
        )
        self.assertTrue(growth_result["advisory"])
        # 그러나 GROWTH는 워크플로우 단계가 아니다
        self.assertNotIn("GROWTH", [s.name for s in StageName])
        self.assertNotIn("GROWTH", self.summary["completed_stages"])

    def test_ai_evolution_outputs_and_validation(self):
        folder = self.project_path / "ai_evolution"
        for name in ("ai_evolution_report.json", "system_reflection.json", "evolution_backlog.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        engine = AIEvolutionEngine()
        self.assertTrue(engine.validate_ai_evolution_report(self.project_path))
        report = engine.load_ai_evolution_report(self.project_path)
        self.assertFalse(report["memory_update_required"])
        self.assertFalse(report["code_change_required"])

    def test_growth_outputs_and_validation(self):
        folder = self.project_path / "analytics"
        for name in ("growth_report.json", "growth_hypotheses.json", "growth_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        engine = GrowthEngine()
        self.assertTrue(engine.validate_growth_report(self.project_path))
        report = engine.load_growth_report(self.project_path)
        self.assertFalse(report["data_ready"])
        self.assertEqual(
            report["causal_path"],
            ["quality", "retention", "recommendation", "views", "subscribers", "revenue"],
        )

    def test_run_report_generator(self):
        reporter = RunReportGenerator()
        report = reporter.create_run_report(self.project_path)
        folder = self.project_path / "reports"
        for name in ("run_report.json", "output_inventory.json", "final_status_summary.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        self.assertTrue(reporter.validate_run_report(self.project_path))
        self.assertFalse(report["production_ready"])
        self.assertFalse(report["upload_ready"])
        self.assertFalse(report["real_assets_present"])
        # 전체 dummy 파이프라인이 완주했으므로 누락 산출물이 없어야 한다
        self.assertEqual(report["missing_expected_outputs"], [])
        self.assertGreater(report["total_outputs_detected"], 40)

    def test_output_summary(self):
        outputs = self.runner.get_output_summary(self.project_path)
        for key, info in outputs.items():
            self.assertTrue(info["exists"], f"산출물 누락: {key} ({info['path']})")


class TestProviders(unittest.TestCase):
    def test_placeholder_providers_do_not_call_external(self):
        cases = [
            (MidjourneyProvider(), "midjourney", "image"),
            (MidjourneyVideoProvider(), "midjourney_video", "video"),
            (TypecastProvider(), "typecast", "voice"),
        ]
        for provider, name, ptype in cases:
            job = provider.create_job({"dummy": True})
            self.assertEqual(job["provider_name"], name)
            self.assertEqual(job["provider_type"], ptype)
            self.assertEqual(job["status"], "NOT_SUBMITTED")
            self.assertFalse(job["external_call_made"])
            status = provider.get_job_status(job["job_id"])
            self.assertFalse(status["external_call_made"])
            result = provider.fetch_result(job["job_id"])
            self.assertIsNone(result["result"])
            self.assertFalse(result["external_call_made"])


class TestManualAssetImporter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_pm(Path(self.tmp.name))
        project = FullPipelineRunner(self.pm).create_sample_project()
        self.project_path = Path(project["path"])
        self.importer = ManualAssetImporter()

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_import_plan_and_manifest(self):
        self.importer.create_import_plan(self.project_path)
        self.assertTrue(self.importer.plan_path(self.project_path).is_file())
        self.assertTrue(self.importer.manifest_path(self.project_path).is_file())
        manifest = self.importer.load_manual_asset_manifest(self.project_path)
        self.assertEqual(manifest["assets"], [])

    def test_register_records_metadata_without_copying(self):
        self.importer.create_import_plan(self.project_path)
        fake_source = str(Path(self.tmp.name) / "my_image.png")  # 존재하지 않는 경로
        item = self.importer.register_manual_asset(
            self.project_path, "image", fake_source, "SC001_hero.png",
            metadata={"scene_id": "SC001"},
        )
        self.assertEqual(item["asset_id"], "MA001")
        self.assertFalse(item["copied"])
        self.assertFalse(item["production_ready"])
        # 파일이 실제로 복사되지 않았는지 확인
        self.assertFalse((self.project_path / "assets" / "SC001_hero.png").exists())
        self.assertTrue(self.importer.validate_manual_asset_manifest(self.project_path))
        manifest = self.importer.load_manual_asset_manifest(self.project_path)
        self.assertEqual(len(manifest["assets"]), 1)
        self.assertEqual(manifest["assets"][0]["metadata"]["scene_id"], "SC001")


class TestZDocsUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        current = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(current, _DOCS_SNAPSHOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
