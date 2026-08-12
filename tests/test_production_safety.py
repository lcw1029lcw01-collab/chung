# -*- coding: utf-8 -*-
"""Production 안전 규칙 테스트 — placeholder 차단·점수 조작 금지·승인 게이트·외부 차단.

실행: 프로젝트 루트에서  python -m unittest tests.test_production_safety -v
"""
import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import write_yaml  # noqa: E402
from engines.quality.production_quality_gate import ProductionQualityGate  # noqa: E402
from engines.workflow import ProductionWorkflowEngine, scan_for_placeholders  # noqa: E402
from tests.production_test_utils import (  # noqa: E402
    good_research_result,
    make_production_project,
    make_temp_root,
    mini_pipeline_stages,
    write_mini_template,
)


class SafetyBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pm = make_temp_root(self.root)

    def tearDown(self):
        self.tmp.cleanup()


class TestPlaceholderRejection(SafetyBase):
    def test_scan_detects_markers(self):
        hits = scan_for_placeholders({
            "a": "This is a placeholder value",
            "b": {"c": ["실제 내용", "더미 데이터"]},
        })
        self.assertEqual(len(hits), 2)

    def test_placeholder_creative_result_rejected(self):
        write_mini_template(self.pm)
        proj = make_production_project(self.pm)
        engine = ProductionWorkflowEngine(proj, root=self.root)
        engine.run_until_gate()
        bad = dict(good_research_result())
        bad["recommendation"] = "TODO: 나중에 채우기"
        f = self.root / "_bad.json"
        f.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
        state = engine.import_result("T_RESEARCH", f)
        step = state["step_states"]["T_RESEARCH"]
        self.assertEqual(step["status"], "FAILED")
        self.assertIn("placeholder", step["error"])
        # 산출물 파일이 만들어지지 않아야 한다
        self.assertFalse((proj / "research/opportunity_research.json").is_file())


class TestNoFabricatedScores(SafetyBase):
    def test_gate_never_passes_without_evidence(self):
        """검증 근거가 없으면 PASS가 아니라 BLOCKED/HUMAN_REVIEW다."""
        gate = ProductionQualityGate()
        report = gate.assess(
            self.root, quality_rules={}, video_rel=None,
        )
        self.assertEqual(report["result"], "BLOCKED")  # 최종 영상 없음 = BLOCKER
        self.assertNotIn("total_score", report)
        self.assertNotIn("score", report)

    def test_gate_requires_human_review_when_unassessed(self):
        video = self.root / "video.mp4"
        video.write_bytes(b"\x00" * 1024)
        gate = ProductionQualityGate(ffprobe="nonexistent_ffprobe_binary")
        report = gate.assess(
            self.root, quality_rules={}, video_rel="video.mp4",
            strategy=None, script=None, research=None,
        )
        self.assertIn(report["result"], ("HUMAN_REVIEW_REQUIRED", "REVISION_REQUIRED"))
        self.assertNotEqual(report["result"], "PASS")
        self.assertTrue(report["unassessed"])

    def test_dummy_quality_engine_not_used_in_production(self):
        """production 파이프라인 stage 정의에 dummy 95점 엔진이 없다."""
        from engines.workflow.executors import build_default_registry
        from engines.quality.quality_engine import QualityEngine

        registry = build_default_registry()
        handler = registry.get("longform.quality_safety")
        import inspect
        source = inspect.getsource(handler)
        self.assertNotIn("create_dummy_quality_report", source)
        self.assertIn("ProductionQualityGate", source)


class TestApprovalGates(SafetyBase):
    def test_no_package_or_publish_without_approval(self):
        """승인 기록 없이 게이트를 통과할 수 없다."""
        write_mini_template(self.pm)
        proj = make_production_project(self.pm)
        engine = ProductionWorkflowEngine(proj, root=self.root)
        engine.run_until_gate()
        f = self.root / "_r.json"
        f.write_text(json.dumps(good_research_result(), ensure_ascii=False), encoding="utf-8")
        engine.import_result("T_RESEARCH", f)
        state = engine.run_until_gate()
        # 게이트 도달 — 승인 없이는 어떤 실행으로도 다음 단계로 못 간다
        for _ in range(3):
            state = engine.run_until_gate()
        self.assertEqual(state["current_stage"], "T_GATE")
        self.assertEqual(state["step_states"]["T_ASSETS"]["status"], "PENDING")
        self.assertEqual(state["approvals"], [])


class TestExternalCallBlocking(SafetyBase):
    def _external_template(self):
        stages = mini_pipeline_stages()
        stages[3]["external_side_effect"] = True  # T_ASSETS를 외부 호출 선언으로
        write_mini_template(self.pm, stages=stages)

    def _advance_to_assets(self, engine):
        engine.run_until_gate()
        f = self.root / "_r.json"
        f.write_text(json.dumps(good_research_result(), ensure_ascii=False), encoding="utf-8")
        engine.import_result("T_RESEARCH", f)
        engine.run_until_gate()
        engine.approve("T_GATE", "APPROVE")
        return engine.run_until_gate()

    def test_external_stage_blocked_by_default(self):
        """외부 호출 stage는 config+플래그 없이는 차단된다."""
        self._external_template()
        proj = make_production_project(self.pm)
        engine = ProductionWorkflowEngine(proj, root=self.root)
        state = self._advance_to_assets(engine)
        step = state["step_states"]["T_ASSETS"]
        self.assertEqual(step["status"], "BLOCKED")
        self.assertIn("external call 차단됨", step["blocker"])

    def test_external_stage_blocked_with_flag_but_no_config(self):
        self._external_template()
        proj = make_production_project(self.pm)
        engine = ProductionWorkflowEngine(proj, root=self.root)
        engine.run_until_gate()
        f = self.root / "_r.json"
        f.write_text(json.dumps(good_research_result(), ensure_ascii=False), encoding="utf-8")
        engine.import_result("T_RESEARCH", f)
        engine.run_until_gate()
        engine.approve("T_GATE", "APPROVE")
        state = engine.run_until_gate(allow_external=True)  # config 없음 → 여전히 차단
        self.assertEqual(state["step_states"]["T_ASSETS"]["status"], "BLOCKED")

    def test_external_stage_runs_with_config_and_flag(self):
        self._external_template()
        write_yaml(self.pm.config / "ados.yaml", {"allow_external_calls": True})
        proj = make_production_project(self.pm)
        engine = ProductionWorkflowEngine(proj, root=self.root)
        engine.run_until_gate()
        f = self.root / "_r.json"
        f.write_text(json.dumps(good_research_result(), ensure_ascii=False), encoding="utf-8")
        engine.import_result("T_RESEARCH", f)
        engine.run_until_gate()
        engine.approve("T_GATE", "APPROVE")
        state = engine.run_until_gate(allow_external=True)
        # 차단 대신 provider 작업 생성 후 외부 결과 대기 (실제 호출은 여전히 없음)
        self.assertEqual(state["step_states"]["T_ASSETS"]["status"], "WAITING_EXTERNAL")


class TestNoNetworkDuringTests(SafetyBase):
    def test_full_mini_workflow_makes_no_network_calls(self):
        """워크플로우 전체 실행 동안 소켓 연결이 한 번도 열리지 않는다."""
        write_mini_template(self.pm)
        proj = make_production_project(self.pm)

        def forbidden(*args, **kwargs):
            raise AssertionError("테스트 중 네트워크 호출 발생")

        with mock.patch.object(socket.socket, "connect", forbidden):
            engine = ProductionWorkflowEngine(proj, root=self.root)
            engine.run_until_gate()
            f = self.root / "_r.json"
            f.write_text(json.dumps(good_research_result(), ensure_ascii=False),
                         encoding="utf-8")
            engine.import_result("T_RESEARCH", f)
            engine.run_until_gate()
            engine.approve("T_GATE", "APPROVE")
            state = engine.run_until_gate()
        self.assertEqual(state["step_states"]["T_ASSETS"]["status"], "WAITING_EXTERNAL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
