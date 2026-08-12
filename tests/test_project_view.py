# -*- coding: utf-8 -*-
"""Project view model 테스트 — 템플릿 기반 탭·진행률·next action·하드코딩 금지.

실행: 프로젝트 루트에서  python -m unittest tests.test_project_view -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.project import ProjectViewBuilder  # noqa: E402
from engines.workflow import ProductionWorkflowEngine  # noqa: E402
from tests.production_test_utils import (  # noqa: E402
    good_research_result,
    make_production_project,
    make_temp_root,
    mini_view,
    write_mini_template,
)


class ViewBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pm = make_temp_root(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def load_view(self, proj: Path) -> dict:
        return json.loads((proj / "ui/project_view.json").read_text(encoding="utf-8"))


class TestTabsFromTemplate(ViewBase):
    def test_tabs_follow_template_config(self):
        write_mini_template(self.pm)
        proj = make_production_project(self.pm)
        view = self.load_view(proj)
        self.assertEqual([t["id"] for t in view["tabs"]], ["overview", "work"])
        self.assertEqual(view["view_id"], "mini_view")

    def test_different_template_different_tabs(self):
        custom_view = mini_view()
        custom_view["view_id"] = "another_view"
        custom_view["tabs"] = [custom_view["tabs"][1]]  # work 탭만
        write_mini_template(self.pm, view=custom_view)
        proj = make_production_project(self.pm)
        view = self.load_view(proj)
        self.assertEqual([t["id"] for t in view["tabs"]], ["work"])

    def test_kpi_resolved_from_project_inputs(self):
        write_mini_template(self.pm)
        proj = make_production_project(self.pm, duration=900)
        view = self.load_view(proj)
        kpi = {k["key"]: k["value"] for k in view["kpis"]}
        self.assertEqual(kpi["target_duration_seconds"], 900)


class TestViewReflectsState(ViewBase):
    def test_progress_blockers_next_action_update(self):
        write_mini_template(self.pm)
        proj = make_production_project(self.pm)
        view = self.load_view(proj)
        self.assertEqual(view["workflow"]["progress"]["completed"], 0)
        self.assertEqual(view["next_action"]["action"], "RUN")

        engine = ProductionWorkflowEngine(proj, root=self.root)
        engine.run_until_gate()
        view = self.load_view(proj)
        self.assertEqual(view["workflow"]["progress"]["completed"], 1)
        self.assertEqual(view["next_action"]["action"], "IMPORT_RESULT")
        self.assertEqual(view["next_action"]["stage"], "T_RESEARCH")

        f = self.root / "_r.json"
        f.write_text(json.dumps(good_research_result(), ensure_ascii=False), encoding="utf-8")
        engine.import_result("T_RESEARCH", f)
        engine.run_until_gate()
        view = self.load_view(proj)
        self.assertEqual(view["workflow"]["progress"]["completed"], 2)
        self.assertEqual(view["next_action"]["action"], "APPROVE")

        engine.approve("T_GATE", "REJECT", notes="테스트 기각")
        view = self.load_view(proj)
        self.assertTrue(any(b.get("type") == "REJECTED" for b in view["blockers"]))

    def test_artifacts_and_approvals_in_view(self):
        write_mini_template(self.pm)
        proj = make_production_project(self.pm)
        engine = ProductionWorkflowEngine(proj, root=self.root)
        engine.run_until_gate()
        f = self.root / "_r.json"
        f.write_text(json.dumps(good_research_result(), ensure_ascii=False), encoding="utf-8")
        engine.import_result("T_RESEARCH", f)
        engine.run_until_gate()
        engine.approve("T_GATE", "APPROVE", reviewer="tester")
        view = self.load_view(proj)
        self.assertIn("opportunity_research", view["artifacts"])
        self.assertEqual(view["approvals"][-1]["reviewer"], "tester")


class TestNoHardcodedProjectNames(unittest.TestCase):
    def test_production_engine_code_has_no_specific_names(self):
        """새 production 코드에 특정 채널/에피소드/사용자 경로 하드코딩이 없다."""
        banned = ["civilization_2100", "civ2100", "million-year", "C:\\\\Users", "이충원"]
        files = [
            "engines/workflow/production_workflow.py",
            "engines/workflow/executors.py",
            "engines/workflow/executor_registry.py",
            "engines/composition/longform_composition.py",
            "engines/quality/production_quality_gate.py",
            "engines/project/project_view_builder.py",
            "engines/project/artifact_index.py",
            "engines/project/runtime_records.py",
            "engines/template/template_bundle.py",
            "scripts/ados.py",
        ]
        for rel in files:
            source = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
            for name in banned:
                self.assertNotIn(name, source, f"{rel}에 '{name}' 하드코딩")


if __name__ == "__main__":
    unittest.main(verbosity=2)
