# -*- coding: utf-8 -*-
"""Production 프로젝트 생성 테스트 — snapshot·입력 검증·길이 규칙·레거시 호환.

실행: 프로젝트 루트에서  python -m unittest tests.test_production_project -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSValidationError, load_yaml, write_yaml  # noqa: E402
from engines.channel import ChannelEngine  # noqa: E402
from engines.project import ProjectEngine  # noqa: E402
from tests.production_test_utils import (  # noqa: E402
    MINI_TEMPLATE_ID,
    make_production_project,
    make_temp_root,
    write_mini_template,
)


class ProductionProjectBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pm = make_temp_root(Path(self.tmp.name))
        write_mini_template(self.pm)

    def tearDown(self):
        self.tmp.cleanup()


class TestSnapshotCreation(ProductionProjectBase):
    def test_creates_snapshot_and_runtime_files(self):
        proj = make_production_project(self.pm)
        for rel in (
            "workflow/pipeline_snapshot.json",
            "workflow/template_bundle_snapshot.json",
            "workflow/workflow_state.json",
            "runtime/artifact_index.json",
            "runtime/cost_ledger.jsonl",
            "runtime/events.jsonl",
            "ui/project_view.json",
            "reports/decision_records.json",
        ):
            self.assertTrue((proj / rel).is_file(), f"누락: {rel}")
        project = json.loads((proj / "project.json").read_text(encoding="utf-8"))
        self.assertEqual(project["template_id"], MINI_TEMPLATE_ID)
        self.assertEqual(project["pipeline_id"], "mini_pipeline_v1")
        self.assertEqual(project["content_type"], "test_content")
        self.assertTrue(project["production_mode"])
        self.assertIn("project_inputs", project)
        state = json.loads((proj / "workflow/workflow_state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_stage"], "T_INTAKE")
        self.assertIn("pipeline_snapshot_hash", state)
        self.assertEqual(set(state["step_states"]),
                         {"T_INTAKE", "T_RESEARCH", "T_GATE", "T_ASSETS"})

    def test_snapshot_immutable_after_template_change(self):
        proj = make_production_project(self.pm)
        snapshot_before = (proj / "workflow/pipeline_snapshot.json").read_text(encoding="utf-8")
        # 템플릿 원본 변경 (stage 제목 수정)
        pipeline_path = self.pm.templates / MINI_TEMPLATE_ID / "pipeline.yaml"
        pipeline = load_yaml(pipeline_path)
        pipeline["stages"][0]["title"] = "변경된 제목"
        write_yaml(pipeline_path, pipeline)
        snapshot_after = (proj / "workflow/pipeline_snapshot.json").read_text(encoding="utf-8")
        self.assertEqual(snapshot_before, snapshot_after)
        snap = json.loads(snapshot_after)
        self.assertEqual(snap["stages"][0]["title"], "접수")


class TestInputValidation(ProductionProjectBase):
    def _create(self, **overrides):
        request = {
            "channel_id": "test_channel", "topic": "주제",
            "target_languages": ["ko"], "duration_seconds": 900,
            "production_mode": True,
        }
        request.update(overrides)
        if not (self.pm.channels / "test_channel" / "channel.yaml").is_file():
            ChannelEngine(self.pm).create_channel({
                "channel_id": "test_channel", "channel_name": "T",
                "template_id": MINI_TEMPLATE_ID, "language": "ko",
            })
        return ProjectEngine(self.pm).create_project(request)

    def test_invalid_enum_input_fails(self):
        with self.assertRaises(ADOSValidationError):
            self._create(project_inputs={"factuality_mode": "make_things_up"})

    def test_recommended_range_warning(self):
        result = self._create(duration_seconds=300)  # 권장 600~1200 밖, 허용 내
        self.assertTrue(any("권장 범위" in w for w in result["input_warnings"]))

    def test_hard_maximum_exceeded_fails(self):
        with self.assertRaises(ADOSValidationError):
            self._create(duration_seconds=2400)  # hard max 1800 초과

    def test_within_recommended_no_warning(self):
        result = self._create(duration_seconds=900)
        self.assertEqual(result["input_warnings"], [])


class TestLegacyCompat(ProductionProjectBase):
    def test_legacy_create_project_unchanged(self):
        """production_mode 없는 기존 호출은 production 파일을 만들지 않는다."""
        ChannelEngine(self.pm).create_channel({
            "channel_id": "legacy_channel", "channel_name": "L",
            "template_id": MINI_TEMPLATE_ID, "language": "ko",
        })
        result = ProjectEngine(self.pm).create_project({
            "channel_id": "legacy_channel", "topic": "레거시 주제",
            "target_languages": ["ko"], "duration_seconds": 900,
        })
        proj = Path(result["path"])
        self.assertTrue((proj / "project.json").is_file())
        self.assertFalse((proj / "workflow/pipeline_snapshot.json").is_file())
        self.assertFalse((proj / "workflow/workflow_state.json").is_file())
        self.assertFalse((proj / "ui/project_view.json").is_file())
        project = json.loads((proj / "project.json").read_text(encoding="utf-8"))
        self.assertNotIn("production_mode", project)
        self.assertEqual(project["status"], "INITIALIZED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
