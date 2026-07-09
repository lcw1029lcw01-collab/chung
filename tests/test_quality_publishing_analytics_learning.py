# -*- coding: utf-8 -*-
"""Quality → Publishing → Analytics → Learning walking skeleton 테스트.

규칙: 임시 루트만 사용, 실제 channels/·projects/에 산출물을 만들지 않는다.
실행: 프로젝트 루트에서
  python -m unittest tests.test_quality_publishing_analytics_learning -v
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
    StageName,
    load_json,
    write_json,
)
from engines.analytics import AnalyticsEngine  # noqa: E402
from engines.channel import ChannelEngine  # noqa: E402
from engines.direction import DirectionEngine  # noqa: E402
from engines.editing import EditingEngine  # noqa: E402
from engines.knowledge import KnowledgeEngine  # noqa: E402
from engines.learning import LearningEngine  # noqa: E402
from engines.motion import MotionEngine  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402
from engines.publishing import PublishingEngine  # noqa: E402
from engines.quality import QualityEngine  # noqa: E402
from engines.research import ResearchEngine  # noqa: E402
from engines.story import StoryEngine  # noqa: E402
from engines.subtitle import SubtitleEngine  # noqa: E402
from engines.timeline import TimelineEngine  # noqa: E402
from engines.visual import VisualEngine  # noqa: E402
from engines.voice import VoiceEngine  # noqa: E402
from engines.workflow import WorkflowOrchestrator, WorkflowStateManager  # noqa: E402

DOCS_DIR = PROJECT_ROOT / "docs"
_DOCS_SNAPSHOT = sorted(
    (p.name, p.stat().st_size, p.stat().st_mtime_ns)
    for p in DOCS_DIR.rglob("*.md")
)

SAMPLE_TEMPLATE_YAML = (
    PROJECT_ROOT / "templates" / "future_documentary_template" / "template.yaml"
)


def make_project_in_temp_root(tmp: Path) -> Path:
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    dst = tmp / "templates" / "future_documentary_template"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(SAMPLE_TEMPLATE_YAML, dst / "template.yaml")
    pm = ADOSPathManager(tmp)
    ChannelEngine(pm).create_channel(
        {
            "channel_id": "future",
            "channel_name": "Future Lab",
            "template_id": "future_documentary_template",
            "language": "ko",
        }
    )
    result = ProjectEngine(pm).create_project(
        {
            "channel_id": "future",
            "topic": "100만 년 후 인간은 어떤 모습일까?",
            "topic_slug": "million-year-human",
            "target_languages": ["ko", "en"],
            "duration_seconds": 900,
        }
    )
    return Path(result["path"])


def run_pipeline_through_editing(project_path: Path) -> None:
    """R→K→S→D→T→V→M→Vo→Sub→E 더미 산출물을 전부 만든다."""
    ResearchEngine().create_dummy_research(project_path)
    KnowledgeEngine().create_dummy_knowledge(project_path)
    StoryEngine().create_dummy_story(project_path)
    DirectionEngine().create_dummy_direction(project_path)
    TimelineEngine().create_dummy_timeline(project_path)
    VisualEngine().create_dummy_visual_plan(project_path)
    MotionEngine().create_dummy_motion_plan(project_path)
    VoiceEngine().create_dummy_voice_plan(project_path)
    SubtitleEngine().create_dummy_subtitle_plan(project_path)
    EditingEngine().create_dummy_editing_plan(project_path)


class PipelineBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project_path = make_project_in_temp_root(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()


class TestQualityEngine(PipelineBase):
    def test_requires_editing_and_asset_plans(self):
        with self.assertRaises(ADOSFileNotFoundError):
            QualityEngine().create_dummy_quality_report(self.project_path)

    def test_dummy_quality_creates_files_and_validates(self):
        run_pipeline_through_editing(self.project_path)
        engine = QualityEngine()
        report = engine.create_dummy_quality_report(self.project_path)
        folder = self.project_path / "reports"
        for name in ("quality_report.json", "quality_gate.json", "quality_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        self.assertTrue(engine.validate_quality_report(self.project_path))
        self.assertEqual(report["total_score"], 95)
        self.assertEqual(report["decision"], "PASS")
        self.assertFalse(report["production_ready"])

    def test_quality_gate_pass_and_no_auto_fix(self):
        run_pipeline_through_editing(self.project_path)
        QualityEngine().create_dummy_quality_report(self.project_path)
        gate = load_json(self.project_path / "reports" / "quality_gate.json")
        self.assertEqual(gate["gate_result"], "PASS")
        self.assertFalse(gate["auto_fix_required"])
        self.assertEqual(gate["next_action"], "PACKAGE")


class TestPublishingEngine(PipelineBase):
    def _prepare_quality(self):
        run_pipeline_through_editing(self.project_path)
        QualityEngine().create_dummy_quality_report(self.project_path)

    def test_package_requires_quality_gate(self):
        run_pipeline_through_editing(self.project_path)
        with self.assertRaises(ADOSFileNotFoundError):
            PublishingEngine().create_dummy_package(self.project_path)

    def test_package_refuses_non_pass_gate(self):
        self._prepare_quality()
        gate_path = self.project_path / "reports" / "quality_gate.json"
        gate = load_json(gate_path)
        gate["gate_result"] = "FAIL"
        write_json(gate_path, gate)
        with self.assertRaises(ADOSValidationError):
            PublishingEngine().create_dummy_package(self.project_path)

    def test_package_creates_files(self):
        self._prepare_quality()
        engine = PublishingEngine()
        manifest = engine.create_dummy_package(self.project_path)
        folder = self.project_path / "package"
        for name in ("package_manifest.json", "upload_package.json", "publishing_plan.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        self.assertTrue(engine.validate_publishing_package(self.project_path))
        self.assertIsNone(manifest["final_video_file"])
        self.assertFalse(manifest["production_ready"])
        plan = load_json(folder / "publishing_plan.json")
        self.assertFalse(plan["upload_ready"])

    def test_ready_state(self):
        self._prepare_quality()
        engine = PublishingEngine()
        engine.create_dummy_package(self.project_path)
        ready = engine.create_dummy_ready_state(self.project_path)
        self.assertTrue(engine.ready_state_path(self.project_path).is_file())
        self.assertEqual(ready["status"], "DUMMY_READY_ONLY")
        self.assertFalse(ready["upload_ready"])
        self.assertTrue(ready["real_upload_blocked"])

    def test_published_record(self):
        self._prepare_quality()
        engine = PublishingEngine()
        engine.create_dummy_package(self.project_path)
        engine.create_dummy_ready_state(self.project_path)
        record = engine.create_dummy_published_record(self.project_path)
        self.assertEqual(record["publication_status"], "SIMULATED_NOT_UPLOADED")
        self.assertIsNone(record["video_url"])
        self.assertIsNone(record["uploaded_at"])


class TestAnalyticsEngine(PipelineBase):
    def _prepare_published(self):
        run_pipeline_through_editing(self.project_path)
        QualityEngine().create_dummy_quality_report(self.project_path)
        publishing = PublishingEngine()
        publishing.create_dummy_package(self.project_path)
        publishing.create_dummy_ready_state(self.project_path)
        publishing.create_dummy_published_record(self.project_path)

    def test_requires_published_record(self):
        with self.assertRaises(ADOSFileNotFoundError):
            AnalyticsEngine().create_dummy_analytics(self.project_path)

    def test_dummy_analytics_creates_files_and_validates(self):
        self._prepare_published()
        engine = AnalyticsEngine()
        snapshot = engine.create_dummy_analytics(self.project_path)
        folder = self.project_path / "analytics"
        for name in ("analytics_plan.json", "performance_snapshot.json", "analytics_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        self.assertTrue(engine.validate_analytics(self.project_path))
        self.assertFalse(snapshot["data_ready"])
        self.assertEqual(snapshot["views"], 0)
        self.assertEqual(snapshot["publication_status"], "SIMULATED_NOT_UPLOADED")


class TestLearningEngine(PipelineBase):
    def test_requires_snapshot(self):
        with self.assertRaises(ADOSFileNotFoundError):
            LearningEngine().create_dummy_learning_report(self.project_path)

    def test_dummy_learning_creates_files_and_validates(self):
        run_pipeline_through_editing(self.project_path)
        QualityEngine().create_dummy_quality_report(self.project_path)
        publishing = PublishingEngine()
        publishing.create_dummy_package(self.project_path)
        publishing.create_dummy_ready_state(self.project_path)
        publishing.create_dummy_published_record(self.project_path)
        AnalyticsEngine().create_dummy_analytics(self.project_path)
        engine = LearningEngine()
        report = engine.create_dummy_learning_report(self.project_path)
        folder = self.project_path / "learning"
        for name in ("learning_report.json", "improvement_backlog.json", "learning_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        self.assertTrue(engine.validate_learning_report(self.project_path))
        self.assertFalse(report["data_ready"])
        self.assertFalse(report["memory_update_required"])


class TestPipelineWorkflow(PipelineBase):
    def test_quality_to_ai_evolution_flow(self):
        """QUALITY → AUTO_FIX → PACKAGE → READY → PUBLISHED → ANALYTICS
        → LEARNING → AI_EVOLUTION 전환 + stage result 기록."""
        orchestrator = WorkflowOrchestrator()
        orchestrator.initialize_workflow(self.project_path)
        run_pipeline_through_editing(self.project_path)
        WorkflowStateManager.set_current_stage(self.project_path, str(StageName.QUALITY))

        publishing = PublishingEngine()
        stages_and_engines = [
            (StageName.QUALITY, lambda: QualityEngine().create_dummy_quality_report(self.project_path)),
            (StageName.AUTO_FIX, lambda: None),  # gate PASS → skip
            (StageName.PACKAGE, lambda: publishing.create_dummy_package(self.project_path)),
            (StageName.READY, lambda: publishing.create_dummy_ready_state(self.project_path)),
            (StageName.PUBLISHED, lambda: publishing.create_dummy_published_record(self.project_path)),
            (StageName.ANALYTICS, lambda: AnalyticsEngine().create_dummy_analytics(self.project_path)),
            (StageName.LEARNING, lambda: LearningEngine().create_dummy_learning_report(self.project_path)),
        ]
        for stage, run in stages_and_engines:
            run()
            result = {"mode": "dummy"}
            if stage == StageName.AUTO_FIX:
                result = {"status": "SKIPPED", "reason": "quality gate PASS"}
            orchestrator.write_stage_result(self.project_path, str(stage), result)
            orchestrator.mark_stage_completed(self.project_path, str(stage))
            orchestrator.advance_to_next_stage(self.project_path)

        self.assertEqual(
            WorkflowStateManager.get_current_stage(self.project_path), "AI_EVOLUTION"
        )
        results_dir = self.project_path / "workflow" / "stage_results"
        for stage in ("QUALITY", "AUTO_FIX", "PACKAGE", "READY",
                      "PUBLISHED", "ANALYTICS", "LEARNING"):
            self.assertTrue(
                (results_dir / f"{stage}_result.json").is_file(),
                f"stage result 누락: {stage}",
            )
        auto_fix = load_json(results_dir / "AUTO_FIX_result.json")
        self.assertEqual(auto_fix["result"]["status"], "SKIPPED")


class TestZDocsUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        current = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(current, _DOCS_SNAPSHOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
