# -*- coding: utf-8 -*-
"""Workflow + Timeline walking skeleton 테스트.

규칙: 임시 루트만 사용, 실제 channels/·projects/에 산출물을 만들지 않는다.
실행: 프로젝트 루트에서  python -m unittest tests.test_workflow_timeline -v
"""
import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import (  # noqa: E402
    ADOSPathManager,
    ADOSValidationError,
    StageName,
    load_json,
)
from engines.channel import ChannelEngine  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402
from engines.timeline import TimelineEngine, TimelineValidator  # noqa: E402
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
    """임시 루트에 채널+프로젝트를 만들고 project 폴더 경로를 돌려준다."""
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


class WorkflowTimelineBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project_path = make_project_in_temp_root(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()


class TestWorkflowState(WorkflowTimelineBase):
    def test_initialize_creates_state_file(self):
        orchestrator = WorkflowOrchestrator()
        state = orchestrator.initialize_workflow(self.project_path)
        state_file = WorkflowStateManager.state_path(self.project_path)
        self.assertTrue(state_file.is_file())
        for key in (
            "project_id", "status", "current_stage",
            "completed_stages", "stage_history", "created_at", "updated_at",
        ):
            self.assertIn(key, state)
        self.assertEqual(state["status"], "RUNNING")

    def test_current_stage_load_and_set(self):
        WorkflowOrchestrator().initialize_workflow(self.project_path)
        self.assertEqual(
            WorkflowStateManager.get_current_stage(self.project_path), "INITIALIZED"
        )
        WorkflowStateManager.set_current_stage(self.project_path, "TIMELINE")
        self.assertEqual(
            WorkflowStateManager.get_current_stage(self.project_path), "TIMELINE"
        )

    def test_stage_result_written(self):
        orchestrator = WorkflowOrchestrator()
        orchestrator.initialize_workflow(self.project_path)
        path = orchestrator.write_stage_result(
            self.project_path, str(StageName.TIMELINE), {"scenes": 3}
        )
        self.assertTrue(path.is_file())
        data = load_json(path)
        self.assertEqual(data["stage"], "TIMELINE")
        self.assertEqual(data["result"]["scenes"], 3)

    def test_advance_to_next_stage(self):
        orchestrator = WorkflowOrchestrator()
        orchestrator.initialize_workflow(self.project_path)
        next_stage = orchestrator.advance_to_next_stage(self.project_path)
        self.assertEqual(next_stage, "RESEARCH")
        self.assertEqual(
            WorkflowStateManager.get_current_stage(self.project_path), "RESEARCH"
        )

    def test_mark_stage_completed(self):
        orchestrator = WorkflowOrchestrator()
        orchestrator.initialize_workflow(self.project_path)
        state = orchestrator.mark_stage_completed(
            self.project_path, "INITIALIZED", result_ref="project.json"
        )
        self.assertIn("INITIALIZED", state["completed_stages"])
        self.assertEqual(state["stage_history"][-1]["status"], "COMPLETED")
        self.assertEqual(state["stage_history"][-1]["notes"], "project.json")


class TestTimelineEngine(WorkflowTimelineBase):
    def test_dummy_timeline_creates_three_files(self):
        TimelineEngine().create_dummy_timeline(self.project_path)
        folder = self.project_path / "timeline"
        self.assertTrue((folder / "timeline.json").is_file())
        self.assertTrue((folder / "timeline_review.json").is_file())
        self.assertTrue((folder / "timeline_lock.json").is_file())

    def test_timeline_content_and_validation(self):
        engine = TimelineEngine()
        timeline = engine.create_dummy_timeline(self.project_path)
        self.assertEqual(len(timeline["scenes"]), 3)
        self.assertEqual(
            [s["scene_id"] for s in timeline["scenes"]], ["SC001", "SC002", "SC003"]
        )
        self.assertEqual(
            [s["purpose"] for s in timeline["scenes"]],
            ["hook", "explanation", "ending"],
        )
        self.assertEqual(
            sum(s["duration_seconds"] for s in timeline["scenes"]),
            timeline["total_duration_seconds"],
        )
        self.assertTrue(engine.validate_timeline(self.project_path))

    def test_lock_timeline(self):
        engine = TimelineEngine()
        engine.create_dummy_timeline(self.project_path)
        lock = engine.lock_timeline(self.project_path)
        self.assertTrue(lock["locked"])
        self.assertIsNotNone(lock["locked_at"])

    def test_duplicate_scene_id_fails(self):
        timeline = TimelineEngine().create_dummy_timeline(self.project_path)
        broken = copy.deepcopy(timeline)
        broken["scenes"][1]["scene_id"] = "SC001"
        with self.assertRaises(ADOSValidationError) as ctx:
            TimelineValidator.validate(broken)
        self.assertIn("중복", str(ctx.exception))

    def test_bad_order_and_duration_fail(self):
        timeline = TimelineEngine().create_dummy_timeline(self.project_path)
        broken = copy.deepcopy(timeline)
        broken["scenes"][2]["order"] = 7
        broken["scenes"][0]["duration_seconds"] = 0
        with self.assertRaises(ADOSValidationError):
            TimelineValidator.validate(broken)


class TestZDocsUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        current = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(current, _DOCS_SNAPSHOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
