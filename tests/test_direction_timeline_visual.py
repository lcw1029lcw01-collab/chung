# -*- coding: utf-8 -*-
"""Direction → Timeline → Visual walking skeleton 테스트.

규칙: 임시 루트만 사용, 실제 channels/·projects/에 산출물을 만들지 않는다.
실행: 프로젝트 루트에서  python -m unittest tests.test_direction_timeline_visual -v
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
from engines.channel import ChannelEngine  # noqa: E402
from engines.direction import DirectionEngine  # noqa: E402
from engines.knowledge import KnowledgeEngine  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402
from engines.research import ResearchEngine  # noqa: E402
from engines.story import StoryEngine  # noqa: E402
from engines.timeline import TimelineEngine  # noqa: E402
from engines.visual import VisualEngine  # noqa: E402
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


def run_story_pipeline(project_path: Path) -> None:
    """Direction의 사전 조건인 R→K→S 더미 산출물을 만든다."""
    ResearchEngine().create_dummy_research(project_path)
    KnowledgeEngine().create_dummy_knowledge(project_path)
    StoryEngine().create_dummy_story(project_path)


class PipelineBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project_path = make_project_in_temp_root(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()


class TestDirectionEngine(PipelineBase):
    def test_requires_story_outputs(self):
        with self.assertRaises(ADOSFileNotFoundError):
            DirectionEngine().create_dummy_direction(self.project_path)

    def test_dummy_direction_creates_files(self):
        run_story_pipeline(self.project_path)
        DirectionEngine().create_dummy_direction(self.project_path)
        folder = self.project_path / "direction"
        for name in ("direction_plan.json", "creative_brief.json", "direction_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")

    def test_direction_validation_passes(self):
        run_story_pipeline(self.project_path)
        engine = DirectionEngine()
        plan = engine.create_dummy_direction(self.project_path)
        self.assertTrue(engine.validate_direction(self.project_path))
        self.assertEqual(plan["direction_mode"], "dummy")
        self.assertEqual(plan["disclaimer"], "Dummy direction plan. Not production-ready.")


class TestTimelineDirectionIntegration(PipelineBase):
    def test_timeline_includes_direction_when_exists(self):
        run_story_pipeline(self.project_path)
        DirectionEngine().create_dummy_direction(self.project_path)
        timeline = TimelineEngine().create_dummy_timeline(self.project_path)
        self.assertEqual(timeline["direction_plan_ref"], "direction/direction_plan.json")
        self.assertIn("pacing", timeline)
        for scene in timeline["scenes"]:
            self.assertIn("visual_style", scene)

    def test_timeline_still_works_without_direction(self):
        timeline = TimelineEngine().create_dummy_timeline(self.project_path)
        self.assertNotIn("direction_plan_ref", timeline)
        self.assertNotIn("pacing", timeline)
        for scene in timeline["scenes"]:
            self.assertNotIn("visual_style", scene)
        self.assertTrue(TimelineEngine().validate_timeline(self.project_path))


class TestVisualEngine(PipelineBase):
    def _prepare_upstream(self, with_timeline=True, with_direction=True):
        run_story_pipeline(self.project_path)
        if with_direction:
            DirectionEngine().create_dummy_direction(self.project_path)
        if with_timeline:
            TimelineEngine().create_dummy_timeline(self.project_path)

    def test_requires_timeline(self):
        self._prepare_upstream(with_timeline=False, with_direction=True)
        with self.assertRaises(ADOSFileNotFoundError):
            VisualEngine().create_dummy_visual_plan(self.project_path)

    def test_requires_direction_plan(self):
        self._prepare_upstream(with_timeline=True, with_direction=False)
        with self.assertRaises(ADOSFileNotFoundError):
            VisualEngine().create_dummy_visual_plan(self.project_path)

    def test_dummy_visual_creates_files(self):
        self._prepare_upstream()
        VisualEngine().create_dummy_visual_plan(self.project_path)
        self.assertTrue(
            (self.project_path / "prompts" / "visual_prompts.json").is_file()
        )
        images = self.project_path / "assets" / "images"
        for name in ("image_manifest.json", "visual_plan.json", "visual_review.json"):
            self.assertTrue((images / name).is_file(), f"누락: {name}")
        manifest = load_json(images / "image_manifest.json")
        self.assertEqual(manifest["images"], [])  # 실제 이미지 없음

    def test_visual_validation_passes(self):
        self._prepare_upstream()
        engine = VisualEngine()
        plan = engine.create_dummy_visual_plan(self.project_path)
        self.assertTrue(engine.validate_visual_plan(self.project_path))
        self.assertFalse(plan["production_ready"])
        self.assertEqual(plan["provider_hint"], "midjourney")
        self.assertEqual(plan["total_scenes"], 3)
        for sv in plan["scene_visuals"]:
            self.assertEqual(sv["status"], "PLANNED")
            self.assertEqual(sv["prompt_mode"], "dummy")


class TestPipelineWorkflow(PipelineBase):
    def test_direction_to_motion_flow(self):
        """DIRECTION → TIMELINE → VISUAL → MOTION 전환 + stage result 기록."""
        orchestrator = WorkflowOrchestrator()
        orchestrator.initialize_workflow(self.project_path)
        run_story_pipeline(self.project_path)
        WorkflowStateManager.set_current_stage(
            self.project_path, str(StageName.DIRECTION)
        )

        stages_and_engines = [
            (StageName.DIRECTION, lambda: DirectionEngine().create_dummy_direction(self.project_path)),
            (StageName.TIMELINE, lambda: TimelineEngine().create_dummy_timeline(self.project_path)),
            (StageName.VISUAL, lambda: VisualEngine().create_dummy_visual_plan(self.project_path)),
        ]
        for stage, run in stages_and_engines:
            run()
            orchestrator.write_stage_result(
                self.project_path, str(stage), {"mode": "dummy"}
            )
            orchestrator.mark_stage_completed(self.project_path, str(stage))
            orchestrator.advance_to_next_stage(self.project_path)

        self.assertEqual(
            WorkflowStateManager.get_current_stage(self.project_path), "MOTION"
        )
        results_dir = self.project_path / "workflow" / "stage_results"
        for stage in ("DIRECTION", "TIMELINE", "VISUAL"):
            self.assertTrue(
                (results_dir / f"{stage}_result.json").is_file(),
                f"stage result 누락: {stage}",
            )


class TestZDocsUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        current = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(current, _DOCS_SNAPSHOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
