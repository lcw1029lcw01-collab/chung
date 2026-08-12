# -*- coding: utf-8 -*-
"""Production workflow 엔진 테스트 — snapshot 순서·게이트·재시도·상태 규칙.

실행: 프로젝트 루트에서  python -m unittest tests.test_production_workflow -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import STAGE_ORDER, ADOSValidationError, write_yaml  # noqa: E402
from engines.workflow import (  # noqa: E402
    ExecutorResult,
    ProductionWorkflowEngine,
    build_default_registry,
)
from tests.production_test_utils import (  # noqa: E402
    MINI_TEMPLATE_ID,
    good_research_result,
    make_production_project,
    make_temp_root,
    mini_pipeline_stages,
    write_mini_template,
)


class WorkflowBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pm = make_temp_root(self.root)
        write_mini_template(self.pm)
        self.proj = make_production_project(self.pm)
        self.engine = ProductionWorkflowEngine(self.proj, root=self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def import_json(self, stage_id: str, data: dict) -> dict:
        f = self.root / f"_{stage_id}_result.json"
        f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return self.engine.import_result(stage_id, f)

    def step(self, state: dict, stage_id: str) -> dict:
        return state["step_states"][stage_id]


class TestStageOrderFromSnapshot(WorkflowBase):
    def test_uses_template_pipeline_order_not_global(self):
        """stage 순서는 전역 STAGE_ORDER가 아니라 pipeline snapshot을 따른다."""
        state = self.engine._load_state()
        snapshot = json.loads(
            (self.proj / state["pipeline_snapshot_ref"]).read_text(encoding="utf-8")
        )
        stage_ids = [s["id"] for s in snapshot["stages"]]
        self.assertEqual(stage_ids, ["T_INTAKE", "T_RESEARCH", "T_GATE", "T_ASSETS"])
        global_names = [str(s) for s in STAGE_ORDER]
        self.assertTrue(all(sid not in global_names for sid in stage_ids))
        self.assertEqual(state["current_stage"], "T_INTAKE")

    def test_run_until_gate_stops_at_creative_waiting(self):
        state = self.engine.run_until_gate()
        self.assertEqual(self.step(state, "T_INTAKE")["status"], "COMPLETED")
        self.assertEqual(state["current_stage"], "T_RESEARCH")
        self.assertEqual(self.step(state, "T_RESEARCH")["status"], "WAITING_INPUT")
        self.assertTrue((self.proj / "workflow/work_orders/T_RESEARCH.json").is_file())


class TestArtifactRequirements(WorkflowBase):
    def test_missing_required_artifact_blocks(self):
        """required artifact가 없으면 실행하지 않고 BLOCKED."""
        state = self.engine._load_state()
        state["current_stage"] = "T_RESEARCH"  # intake 건너뛰고 강제 지정
        self.engine._save_state(state)
        state = self.engine.run_current()
        step = self.step(state, "T_RESEARCH")
        self.assertEqual(step["status"], "BLOCKED")
        self.assertIn("required artifact", step["blocker"])

    def test_undeclared_output_prevents_completion(self):
        """executor가 선언한 output을 만들지 않으면 완료 처리하지 않는다."""
        registry = build_default_registry()
        registry.register("project.intake",
                          lambda ctx: ExecutorResult(status="COMPLETED", outputs={}))
        engine = ProductionWorkflowEngine(self.proj, registry=registry, root=self.root)
        state = engine.run_current()
        step = state["step_states"]["T_INTAKE"]
        self.assertEqual(step["status"], "FAILED")
        self.assertIn("선언된 output 미생산", step["error"])


class TestHumanGate(WorkflowBase):
    def advance_to_gate(self) -> dict:
        self.engine.run_until_gate()
        self.import_json("T_RESEARCH", good_research_result())
        return self.engine.run_until_gate()

    def test_gate_waits_for_explicit_approval(self):
        state = self.advance_to_gate()
        self.assertEqual(state["current_stage"], "T_GATE")
        self.assertEqual(self.step(state, "T_GATE")["status"], "WAITING_APPROVAL")
        # 승인 없이 아무리 실행해도 진행되지 않는다
        state = self.engine.run_until_gate()
        self.assertEqual(self.step(state, "T_GATE")["status"], "WAITING_APPROVAL")

    def test_approve_completes_gate_and_advances(self):
        self.advance_to_gate()
        state = self.engine.approve("T_GATE", "APPROVE", reviewer="tester")
        self.assertEqual(self.step(state, "T_GATE")["status"], "COMPLETED")
        self.assertEqual(state["current_stage"], "T_ASSETS")
        self.assertEqual(state["approvals"][-1]["decision"], "APPROVE")
        self.assertTrue((self.proj / "workflow/approvals/T_GATE_decision.json").is_file())

    def test_request_revision_does_not_advance(self):
        self.advance_to_gate()
        state = self.engine.approve("T_GATE", "REQUEST_REVISION", notes="다시")
        self.assertEqual(self.step(state, "T_GATE")["status"], "PENDING")
        self.assertEqual(state["current_stage"], "T_GATE")

    def test_reject_blocks_workflow(self):
        self.advance_to_gate()
        state = self.engine.approve("T_GATE", "REJECT", notes="기각")
        self.assertEqual(self.step(state, "T_GATE")["status"], "FAILED")
        self.assertEqual(state["status"], "BLOCKED")

    def test_cannot_approve_non_current_stage(self):
        """현재 단계가 아닌 단계를 임의로 완료 처리할 수 없다."""
        self.engine.run_until_gate()  # current = T_RESEARCH
        with self.assertRaises(ADOSValidationError):
            self.engine.approve("T_GATE", "APPROVE")

    def test_cannot_import_to_non_current_stage(self):
        self.engine.run_until_gate()
        f = self.root / "_r.json"
        f.write_text("{}", encoding="utf-8")
        with self.assertRaises(ADOSValidationError):
            self.engine.import_result("T_ASSETS", f)


class TestExternalProviderWait(WorkflowBase):
    def advance_to_assets(self) -> dict:
        self.engine.run_until_gate()
        self.import_json("T_RESEARCH", good_research_result())
        self.engine.run_until_gate()
        self.engine.approve("T_GATE", "APPROVE")
        return self.engine.run_until_gate()

    def test_provider_stage_waits_external_until_import(self):
        state = self.advance_to_assets()
        step = self.step(state, "T_ASSETS")
        self.assertEqual(step["status"], "WAITING_EXTERNAL")
        queue = json.loads((self.proj / "providers/job_queue.json").read_text(encoding="utf-8"))
        self.assertTrue(queue["jobs"])
        self.assertTrue(all(j["external_call_made"] is False for j in queue["jobs"]))
        # 실행을 반복해도 외부 대기 유지
        state = self.engine.run_until_gate()
        self.assertEqual(self.step(state, "T_ASSETS")["status"], "WAITING_EXTERNAL")

    def test_import_with_real_files_completes_and_workflow_completes(self):
        """마지막 단계가 끝났을 때만 COMPLETE가 된다."""
        self.advance_to_assets()
        assets = self.proj / "assets" / "production"
        (assets / "audio").mkdir(parents=True, exist_ok=True)
        (assets / "images").mkdir(parents=True, exist_ok=True)
        (assets / "audio" / "b1.wav").write_bytes(b"\x00" * 64)
        (assets / "images" / "c1.png").write_bytes(b"\x89PNG\r\n" + b"\x00" * 32)
        state = self.import_json("T_ASSETS", {
            "assets_root": "assets/production",
            "blocks": [{"id": "b1", "text": "첫 블록 나레이션",
                        "audio": "audio/b1.wav",
                        "cuts": [{"id": "c1", "image": "images/c1.png"}]}],
        })
        self.assertEqual(self.step(state, "T_ASSETS")["status"], "COMPLETED")
        self.assertEqual(state["status"], "COMPLETE")
        self.assertIsNone(state["current_stage"])

    def test_workflow_not_complete_before_last_stage(self):
        state = self.advance_to_assets()
        self.assertEqual(state["status"], "RUNNING")

    def test_import_missing_files_fails(self):
        self.advance_to_assets()
        state = self.import_json("T_ASSETS", {
            "assets_root": "assets/production",
            "blocks": [{"id": "b1", "text": "블록", "audio": "audio/none.wav",
                        "cuts": [{"id": "c1", "image": "images/none.png"}]}],
        })
        self.assertEqual(self.step(state, "T_ASSETS")["status"], "FAILED")


class TestRetryAndResume(WorkflowBase):
    def test_failed_stage_stays_current_and_retry_resumes(self):
        """실패 시 현재 단계에 머물고, retry 후 재개할 수 있다."""
        self.engine.run_until_gate()
        state = self.import_json("T_RESEARCH", {"competitor_landscape": []})  # 스키마 위반
        step = self.step(state, "T_RESEARCH")
        self.assertEqual(step["status"], "FAILED")
        self.assertEqual(state["current_stage"], "T_RESEARCH")
        self.assertGreaterEqual(step["attempts"], 1)
        # retry → 다시 work order 대기 → 정상 결과 import → 완료
        state = self.engine.retry("T_RESEARCH")
        self.assertEqual(self.step(state, "T_RESEARCH")["status"], "WAITING_INPUT")
        state = self.import_json("T_RESEARCH", good_research_result())
        self.assertEqual(self.step(state, "T_RESEARCH")["status"], "COMPLETED")

    def test_resume_after_error_new_engine_instance(self):
        """오류 후 새 엔진 인스턴스로 resume해도 완료 단계를 다시 실행하지 않는다."""
        self.engine.run_until_gate()
        self.import_json("T_RESEARCH", good_research_result())
        intake_completed_at = self.step(
            self.engine._load_state(), "T_INTAKE")["completed_at"]
        resumed = ProductionWorkflowEngine(self.proj, root=self.root)
        state = resumed.run_until_gate()
        self.assertEqual(self.step(state, "T_INTAKE")["completed_at"], intake_completed_at)
        self.assertEqual(self.step(state, "T_INTAKE")["attempts"], 1)  # 재실행 없음
        self.assertEqual(state["current_stage"], "T_GATE")

    def test_retry_limit_blocks_then_force_reruns(self):
        registry = build_default_registry()
        registry.register("project.intake",
                          lambda ctx: ExecutorResult(status="FAILED", blockers=["의도적 실패"]))
        engine = ProductionWorkflowEngine(self.proj, registry=registry, root=self.root)
        for _ in range(3):
            state = engine.run_current()
            self.assertEqual(state["step_states"]["T_INTAKE"]["status"], "FAILED")
            state = engine._load_state()
            state["step_states"]["T_INTAKE"]["status"] = "PENDING"
            engine._save_state(state)
        state = engine.run_current()  # 4번째 — 한도 초과
        self.assertEqual(state["step_states"]["T_INTAKE"]["status"], "BLOCKED")
        self.assertIn("retry 한도 초과", state["step_states"]["T_INTAKE"]["blocker"])
        # --force는 정상 registry로 재실행
        good_engine = ProductionWorkflowEngine(self.proj, root=self.root)
        state = good_engine.retry("T_INTAKE", force=True)
        self.assertEqual(state["step_states"]["T_INTAKE"]["status"], "COMPLETED")

    def test_force_reruns_completed_stage(self):
        """완료된 단계는 --force가 있을 때만 재실행된다."""
        self.engine.run_until_gate()  # T_INTAKE 완료
        state = self.engine._load_state()
        self.assertEqual(self.step(state, "T_INTAKE")["status"], "COMPLETED")
        with self.assertRaises(ADOSValidationError):
            self.engine.retry("T_INTAKE")  # force 없이 완료 단계 재실행 금지
        state = self.engine.retry("T_INTAKE", force=True)
        self.assertEqual(self.step(state, "T_INTAKE")["status"], "COMPLETED")
        self.assertEqual(self.step(state, "T_INTAKE")["attempts"], 1)  # 리셋 후 1회


if __name__ == "__main__":
    unittest.main(verbosity=2)
