# -*- coding: utf-8 -*-
"""Research → Knowledge → Story walking skeleton 테스트.

규칙: 임시 루트만 사용, 실제 channels/·projects/에 산출물을 만들지 않는다.
실행: 프로젝트 루트에서  python -m unittest tests.test_research_knowledge_story -v
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
from engines.knowledge import KnowledgeEngine  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402
from engines.research import ResearchEngine  # noqa: E402
from engines.story import StoryEngine  # noqa: E402
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


class PipelineBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project_path = make_project_in_temp_root(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()


class TestResearchEngine(PipelineBase):
    def test_dummy_research_creates_files(self):
        ResearchEngine().create_dummy_research(self.project_path)
        folder = self.project_path / "research"
        for name in ("research_brief.json", "research_questions.json", "source_plan.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")

    def test_research_validation_passes(self):
        engine = ResearchEngine()
        brief = engine.create_dummy_research(self.project_path)
        self.assertTrue(engine.validate_research(self.project_path))
        self.assertEqual(brief["research_mode"], "dummy")
        self.assertIn("disclaimer", brief)


class TestKnowledgeEngine(PipelineBase):
    def test_requires_research_output(self):
        with self.assertRaises(ADOSFileNotFoundError):
            KnowledgeEngine().create_dummy_knowledge(self.project_path)

    def test_dummy_knowledge_creates_files(self):
        ResearchEngine().create_dummy_research(self.project_path)
        KnowledgeEngine().create_dummy_knowledge(self.project_path)
        folder = self.project_path / "knowledge"
        for name in ("knowledge_map.json", "fact_sheet.json", "knowledge_gaps.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        fact_sheet = load_json(folder / "fact_sheet.json")
        self.assertFalse(fact_sheet["production_ready"])
        self.assertIn("placeholder", fact_sheet["disclaimer"].lower())

    def test_knowledge_validation_passes(self):
        ResearchEngine().create_dummy_research(self.project_path)
        engine = KnowledgeEngine()
        engine.create_dummy_knowledge(self.project_path)
        self.assertTrue(engine.validate_knowledge(self.project_path))


class TestStoryEngine(PipelineBase):
    def test_requires_knowledge_output(self):
        with self.assertRaises(ADOSFileNotFoundError):
            StoryEngine().create_dummy_story(self.project_path)

    def test_dummy_story_creates_files(self):
        ResearchEngine().create_dummy_research(self.project_path)
        KnowledgeEngine().create_dummy_knowledge(self.project_path)
        StoryEngine().create_dummy_story(self.project_path)
        folder = self.project_path / "story"
        for name in ("story_outline.json", "script_draft.json", "story_review.json"):
            self.assertTrue((folder / name).is_file(), f"누락: {name}")
        draft = load_json(folder / "script_draft.json")
        self.assertEqual(draft["language"], "ko")
        self.assertEqual(draft["disclaimer"], "Dummy script draft. Not production-ready.")
        self.assertEqual(len(draft["narration_blocks"]), 5)

    def test_story_validation_passes(self):
        ResearchEngine().create_dummy_research(self.project_path)
        KnowledgeEngine().create_dummy_knowledge(self.project_path)
        engine = StoryEngine()
        outline = engine.create_dummy_story(self.project_path)
        self.assertTrue(engine.validate_story(self.project_path))
        for key in ("hook", "setup", "development", "payoff", "ending"):
            self.assertIn(key, outline["structure"])


class TestPipelineWorkflow(PipelineBase):
    def test_research_to_direction_flow(self):
        """RESEARCH → KNOWLEDGE → STORY → DIRECTION 상태 전환 + 결과 파일 기록."""
        orchestrator = WorkflowOrchestrator()
        orchestrator.initialize_workflow(self.project_path)
        orchestrator.advance_to_next_stage(self.project_path)  # → RESEARCH
        self.assertEqual(
            WorkflowStateManager.get_current_stage(self.project_path), "RESEARCH"
        )

        stages_and_engines = [
            (StageName.RESEARCH, lambda: ResearchEngine().create_dummy_research(self.project_path)),
            (StageName.KNOWLEDGE, lambda: KnowledgeEngine().create_dummy_knowledge(self.project_path)),
            (StageName.STORY, lambda: StoryEngine().create_dummy_story(self.project_path)),
        ]
        for stage, run in stages_and_engines:
            run()
            orchestrator.write_stage_result(
                self.project_path, str(stage), {"mode": "dummy"}
            )
            orchestrator.mark_stage_completed(self.project_path, str(stage))
            orchestrator.advance_to_next_stage(self.project_path)

        self.assertEqual(
            WorkflowStateManager.get_current_stage(self.project_path), "DIRECTION"
        )
        state = WorkflowStateManager.load_workflow_state(self.project_path)
        self.assertEqual(
            state["completed_stages"], ["RESEARCH", "KNOWLEDGE", "STORY"]
        )
        results_dir = self.project_path / "workflow" / "stage_results"
        for stage in ("RESEARCH", "KNOWLEDGE", "STORY"):
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
