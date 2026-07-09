# -*- coding: utf-8 -*-
"""Motion → Voice → Subtitle → Editing walking skeleton 테스트.

규칙: 임시 루트만 사용, 실제 channels/·projects/에 산출물을 만들지 않는다.
실행: 프로젝트 루트에서  python -m unittest tests.test_motion_voice_subtitle_editing -v
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
from engines.editing import EditingEngine  # noqa: E402
from engines.knowledge import KnowledgeEngine  # noqa: E402
from engines.motion import MotionEngine  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402
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


def run_upstream_pipeline(project_path: Path, through: str = "visual") -> None:
    """R→K→S→D→T→V 순서로 through 단계까지 더미 산출물을 만든다."""
    steps = [
        ("research", lambda: ResearchEngine().create_dummy_research(project_path)),
        ("knowledge", lambda: KnowledgeEngine().create_dummy_knowledge(project_path)),
        ("story", lambda: StoryEngine().create_dummy_story(project_path)),
        ("direction", lambda: DirectionEngine().create_dummy_direction(project_path)),
        ("timeline", lambda: TimelineEngine().create_dummy_timeline(project_path)),
        ("visual", lambda: VisualEngine().create_dummy_visual_plan(project_path)),
    ]
    for name, run in steps:
        run()
        if name == through:
            return


class PipelineBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project_path = make_project_in_temp_root(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()


class TestMotionEngine(PipelineBase):
    def test_requires_visual_and_timeline(self):
        # timeline만 있고 visual_plan 없음
        run_upstream_pipeline(self.project_path, through="timeline")
        with self.assertRaises(ADOSFileNotFoundError):
            MotionEngine().create_dummy_motion_plan(self.project_path)

    def test_dummy_motion_creates_files_and_validates(self):
        run_upstream_pipeline(self.project_path)
        engine = MotionEngine()
        plan = engine.create_dummy_motion_plan(self.project_path)
        folder = self.project_path / "assets" / "motion"
        for name in ("motion_plan.json", "motion_manifest.json", "motion_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        self.assertTrue(engine.validate_motion_plan(self.project_path))
        self.assertFalse(plan["production_ready"])
        self.assertEqual(plan["provider_hint"], "midjourney_video")
        self.assertEqual(load_json(folder / "motion_manifest.json")["clips"], [])
        for sm in plan["scene_motions"]:
            self.assertEqual(sm["status"], "PLANNED")
            self.assertGreater(sm["duration_seconds"], 0)


class TestVoiceEngine(PipelineBase):
    def test_requires_script_and_timeline(self):
        # script는 있지만 timeline 없음
        run_upstream_pipeline(self.project_path, through="story")
        with self.assertRaises(ADOSFileNotFoundError):
            VoiceEngine().create_dummy_voice_plan(self.project_path)

    def test_dummy_voice_creates_files_and_validates(self):
        run_upstream_pipeline(self.project_path, through="timeline")
        engine = VoiceEngine()
        plan = engine.create_dummy_voice_plan(self.project_path)
        folder = self.project_path / "assets" / "audio"
        for name in ("voice_plan.json", "voice_manifest.json", "voice_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        self.assertTrue(engine.validate_voice_plan(self.project_path))
        self.assertFalse(plan["production_ready"])
        self.assertEqual(plan["provider_hint"], "typecast")
        self.assertEqual(plan["language"], "ko")
        self.assertEqual(len(plan["narration_blocks"]), 5)
        self.assertEqual(load_json(folder / "voice_manifest.json")["audio_files"], [])


class TestSubtitleEngine(PipelineBase):
    def test_requires_voice_plan(self):
        run_upstream_pipeline(self.project_path, through="story")
        with self.assertRaises(ADOSFileNotFoundError):
            SubtitleEngine().create_dummy_subtitle_plan(self.project_path)

    def test_dummy_subtitle_creates_files_and_validates(self):
        run_upstream_pipeline(self.project_path, through="timeline")
        VoiceEngine().create_dummy_voice_plan(self.project_path)
        engine = SubtitleEngine()
        plan = engine.create_dummy_subtitle_plan(self.project_path)
        folder = self.project_path / "assets" / "subtitles"
        for name in ("subtitle_plan.json", "subtitle_manifest.json", "subtitle_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        self.assertTrue(engine.validate_subtitle_plan(self.project_path))
        self.assertFalse(plan["production_ready"])
        # ko/en 두 언어 × 5블록 = 10블록, .srt 파일은 없음
        self.assertEqual(len(plan["subtitle_blocks"]), 10)
        self.assertEqual(
            load_json(folder / "subtitle_manifest.json")["subtitle_files"], []
        )
        for sb in plan["subtitle_blocks"]:
            self.assertGreaterEqual(sb["end_seconds"], sb["start_seconds"])


class TestEditingEngine(PipelineBase):
    def test_requires_all_upstream_outputs(self):
        # subtitle_plan만 빠진 상태
        run_upstream_pipeline(self.project_path)
        MotionEngine().create_dummy_motion_plan(self.project_path)
        VoiceEngine().create_dummy_voice_plan(self.project_path)
        with self.assertRaises(ADOSFileNotFoundError):
            EditingEngine().create_dummy_editing_plan(self.project_path)

    def test_dummy_editing_creates_files_and_validates(self):
        run_upstream_pipeline(self.project_path)
        MotionEngine().create_dummy_motion_plan(self.project_path)
        VoiceEngine().create_dummy_voice_plan(self.project_path)
        SubtitleEngine().create_dummy_subtitle_plan(self.project_path)
        engine = EditingEngine()
        plan = engine.create_dummy_editing_plan(self.project_path)
        folder = self.project_path / "edit"
        for name in ("editing_plan.json", "assembly_manifest.json", "editing_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        self.assertTrue(engine.validate_editing_plan(self.project_path))
        self.assertFalse(plan["production_ready"])
        self.assertEqual(plan["estimated_duration_seconds"], 900)
        self.assertEqual(len(plan["assembly_steps"]), 6)
        self.assertEqual(load_json(folder / "assembly_manifest.json")["outputs"], [])
        for step in plan["assembly_steps"]:
            self.assertEqual(step["status"], "PLANNED")


class TestPipelineWorkflow(PipelineBase):
    def test_motion_to_quality_flow(self):
        """MOTION → VOICE → SUBTITLE → EDITING → QUALITY 전환 + stage result 기록."""
        orchestrator = WorkflowOrchestrator()
        orchestrator.initialize_workflow(self.project_path)
        run_upstream_pipeline(self.project_path)
        WorkflowStateManager.set_current_stage(self.project_path, str(StageName.MOTION))

        stages_and_engines = [
            (StageName.MOTION, lambda: MotionEngine().create_dummy_motion_plan(self.project_path)),
            (StageName.VOICE, lambda: VoiceEngine().create_dummy_voice_plan(self.project_path)),
            (StageName.SUBTITLE, lambda: SubtitleEngine().create_dummy_subtitle_plan(self.project_path)),
            (StageName.EDITING, lambda: EditingEngine().create_dummy_editing_plan(self.project_path)),
        ]
        for stage, run in stages_and_engines:
            run()
            orchestrator.write_stage_result(
                self.project_path, str(stage), {"mode": "dummy"}
            )
            orchestrator.mark_stage_completed(self.project_path, str(stage))
            orchestrator.advance_to_next_stage(self.project_path)

        self.assertEqual(
            WorkflowStateManager.get_current_stage(self.project_path), "QUALITY"
        )
        results_dir = self.project_path / "workflow" / "stage_results"
        for stage in ("MOTION", "VOICE", "SUBTITLE", "EDITING"):
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
