# -*- coding: utf-8 -*-
"""Production workflow engine — 템플릿 pipeline snapshot 기반 실행 관리자.

레거시 WorkflowStateManager/WorkflowOrchestrator(전역 STAGE_ORDER 기반)는
데모 호환용으로 그대로 두고, production 프로젝트는 이 엔진을 사용한다.
stage 순서는 프로젝트 생성 시 저장된 workflow/pipeline_snapshot.json을 따른다.

핵심 보장:
- 현재 단계가 아닌 단계를 임의로 완료 처리할 수 없다.
- required artifact가 없으면 실행하지 않는다 (BLOCKED).
- executor가 선언한 output이 실재하지 않으면 완료 처리하지 않는다.
- 실패 시 현재 단계에 머물고 retry 횟수를 기록한다.
- 완료된 정상 단계는 재실행하지 않는다 (--force 제외).
- human gate는 명시적 승인 전까지 진행하지 않는다.
- 외부 작업은 결과 import까지 WAITING_EXTERNAL로 남는다.
- 마지막 단계가 끝났을 때만 COMPLETE가 된다.
- 외부 호출이 선언된 stage는 config 허용 + --allow-external 둘 다 필요.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSPathManager,
    ADOSValidationError,
    load_json,
    load_yaml,
    write_json,
)
from engines.project.artifact_index import ArtifactIndex
from engines.project.runtime_records import CostLedger, EventLog

from .executor_registry import ExecutionContext, ExecutorRegistry
from .executors import APPROVALS_DIR, build_default_registry

STATE_REL = Path("workflow") / "workflow_state.json"

STEP_STATUSES = [
    "PENDING", "RUNNING", "WAITING_INPUT", "WAITING_EXTERNAL",
    "WAITING_APPROVAL", "COMPLETED", "FAILED", "BLOCKED", "SKIPPED",
]

WORKFLOW_RUNNING = "RUNNING"
WORKFLOW_COMPLETE = "COMPLETE"
WORKFLOW_BLOCKED = "BLOCKED"

_DEFAULT_MAX_ATTEMPTS = 3

_MEDIA_TYPES = {
    ".json": "application/json",
    ".mp4": "video/mp4",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".srt": "text/plain",
    ".ass": "text/plain",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_step_state() -> dict:
    return {
        "status": "PENDING",
        "attempts": 0,
        "started_at": None,
        "completed_at": None,
        "input_refs": [],
        "output_refs": {},
        "error": None,
        "blocker": None,
        "estimated_cost": None,
        "actual_cost": None,
    }


def create_production_workflow_state(
    project_path: str | Path, project: dict, snapshot_refs: dict, pipeline_snapshot: dict
) -> dict:
    """production workflow_state.json을 생성한다 (ProjectEngine이 호출)."""
    project_path = Path(project_path)
    state_path = project_path / STATE_REL
    if state_path.is_file():
        raise ADOSValidationError(
            f"workflow_state.json이 이미 존재합니다: {state_path}",
            location="create_production_workflow_state",
        )
    stages = pipeline_snapshot["stages"]
    step_states = {}
    current = None
    for stage in stages:
        step = _new_step_state()
        if stage.get("enabled", True) is False:
            step["status"] = "SKIPPED"
        elif current is None:
            current = stage["id"]
        step_states[stage["id"]] = step
    now = _now_iso()
    state = {
        "project_id": project["project_id"],
        "template_id": snapshot_refs["template_id"] if "template_id" in snapshot_refs
        else pipeline_snapshot.get("template_id"),
        "template_version": snapshot_refs["template_version"],
        "pipeline_id": snapshot_refs["pipeline_id"],
        "pipeline_version": snapshot_refs["pipeline_version"],
        "pipeline_snapshot_ref": snapshot_refs["pipeline_snapshot_ref"],
        "pipeline_snapshot_hash": snapshot_refs["pipeline_snapshot_hash"],
        "status": WORKFLOW_RUNNING,
        "current_stage": current,
        "step_states": step_states,
        "approvals": [],
        "blockers": [],
        "created_at": now,
        "updated_at": now,
    }
    write_json(state_path, state)
    return state


class ProductionWorkflowEngine:
    def __init__(
        self,
        project_path: str | Path,
        registry: ExecutorRegistry | None = None,
        logger: ADOSLogger | None = None,
        root: str | Path | None = None,
    ):
        self.project_path = Path(project_path).resolve()
        self.logger = logger
        self.registry = registry or build_default_registry()
        self.root = Path(root).resolve() if root else ADOSPathManager.find_project_root(
            self.project_path
        )
        project_json = self.project_path / "project.json"
        if not project_json.is_file():
            raise ADOSFileNotFoundError(
                f"project.json이 없습니다: {self.project_path}",
                location="ProductionWorkflowEngine",
            )
        self.project = load_json(project_json)
        if not self.project.get("production_mode"):
            raise ADOSValidationError(
                "production_mode 프로젝트가 아닙니다 — 레거시 데모 프로젝트는 "
                "기존 WorkflowOrchestrator를 사용하세요.",
                location="ProductionWorkflowEngine",
                suggested_fix="scripts/ados.py project create로 프로젝트를 생성하세요.",
            )
        self.artifacts = ArtifactIndex(self.project_path)
        self.costs = CostLedger(self.project_path, self.project["project_id"])
        self.events = EventLog(self.project_path)

    # --- 상태 IO ---
    def _load_state(self) -> dict:
        path = self.project_path / STATE_REL
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"workflow_state.json이 없습니다: {path}",
                location="ProductionWorkflowEngine._load_state",
            )
        return load_json(path)

    def _save_state(self, state: dict) -> dict:
        state["updated_at"] = _now_iso()
        write_json(self.project_path / STATE_REL, state)
        self._refresh_view()
        return state

    def _refresh_view(self) -> None:
        from engines.project.project_view_builder import ProjectViewBuilder

        ProjectViewBuilder(self.project_path).build()

    def _pipeline_snapshot(self) -> dict:
        state = self._load_state()
        return load_json(self.project_path / state["pipeline_snapshot_ref"])

    def _bundle_snapshot(self) -> dict | None:
        path = self.project_path / "workflow" / "template_bundle_snapshot.json"
        return load_json(path) if path.is_file() else None

    def _stage_def(self, pipeline: dict, stage_id: str) -> dict:
        for stage in pipeline["stages"]:
            if stage["id"] == stage_id:
                return stage
        raise ADOSValidationError(
            f"pipeline snapshot에 없는 stage: {stage_id}",
            location="ProductionWorkflowEngine._stage_def",
        )

    # --- 조회 ---
    def status(self) -> dict:
        state = self._load_state()
        pipeline = self._pipeline_snapshot()
        stages = []
        for stage in pipeline["stages"]:
            step = state["step_states"][stage["id"]]
            stages.append({
                "id": stage["id"], "title": stage.get("title"), "kind": stage.get("kind"),
                "owner_role": stage.get("owner_role"),
                "status": step["status"], "attempts": step["attempts"],
                "blocker": step["blocker"], "error": step["error"],
            })
        completed = sum(1 for s in stages if s["status"] == "COMPLETED")
        return {
            "project_id": state["project_id"],
            "workflow_status": state["status"],
            "current_stage": state["current_stage"],
            "progress": {"completed": completed, "total": len(stages)},
            "stages": stages,
            "blockers": state["blockers"],
            "next_action": self.next_action(state, pipeline),
        }

    def next_action(self, state: dict | None = None, pipeline: dict | None = None) -> dict:
        state = state or self._load_state()
        if state["status"] == WORKFLOW_COMPLETE:
            return {"action": "NONE", "description": "workflow 완료"}
        current = state["current_stage"]
        if current is None:
            return {"action": "NONE", "description": "실행할 단계 없음"}
        step = state["step_states"][current]
        base = f"python scripts/ados.py project"
        if step["status"] == "WAITING_APPROVAL":
            return {
                "action": "APPROVE", "stage": current,
                "description": f"사람 승인 대기 — {base} approve <PATH> {current} --decision APPROVE --reviewer human",
            }
        if step["status"] == "WAITING_INPUT":
            return {
                "action": "IMPORT_RESULT", "stage": current,
                "description": f"작업 결과 import 대기 — work order: workflow/work_orders/{current}.json",
            }
        if step["status"] == "WAITING_EXTERNAL":
            return {
                "action": "IMPORT_RESULT", "stage": current,
                "description": f"외부 자산 import 대기 — {base} import-result <PATH> {current} <MANIFEST>",
            }
        if step["status"] in ("FAILED", "BLOCKED"):
            return {
                "action": "RETRY", "stage": current,
                "description": f"실패/차단 — 원인 해결 후 {base} retry <PATH> {current}",
            }
        return {
            "action": "RUN", "stage": current,
            "description": f"다음 단계 실행 — {base} run-until-gate <PATH>",
        }

    # --- 실행 ---
    def _external_allowed(self) -> bool:
        config_path = self.root / "config" / "ados.yaml"
        if not config_path.is_file():
            return False
        config = load_yaml(config_path)
        return bool(isinstance(config, dict) and config.get("allow_external_calls"))

    def _dispatch(self, state: dict, pipeline: dict, stage: dict,
                  imported_result: dict | None = None,
                  imported_ref: str | None = None,
                  allow_external: bool = False, force: bool = False) -> dict:
        stage_id = stage["id"]
        step = state["step_states"][stage_id]

        # 외부 호출 이중 안전장치
        if stage.get("external_side_effect"):
            if not (self._external_allowed() and allow_external):
                step["status"] = "BLOCKED"
                step["blocker"] = (
                    "external call 차단됨 — config allow_external_calls=true와 "
                    "--allow-external 둘 다 필요"
                )
                self.events.append("STAGE_BLOCKED", stage_id, message=step["blocker"])
                return self._save_state(state)

        # required artifact 확인
        missing = [key for key in stage.get("requires") or []
                   if not self.artifacts.exists(key)]
        if missing:
            step["status"] = "BLOCKED"
            step["blocker"] = f"required artifact 없음: {', '.join(missing)}"
            self.events.append("STAGE_BLOCKED", stage_id, message=step["blocker"])
            return self._save_state(state)

        # retry 한도 — 결과 import는 대기 중인 시도의 연속이므로 새 시도로 세지 않는다
        is_import = imported_result is not None
        max_attempts = (stage.get("retry_policy") or {}).get("max_attempts", _DEFAULT_MAX_ATTEMPTS)
        if not force and not is_import and step["attempts"] >= max_attempts:
            step["status"] = "BLOCKED"
            step["blocker"] = f"retry 한도 초과 ({step['attempts']}/{max_attempts}) — --force 필요"
            self.events.append("STAGE_BLOCKED", stage_id, message=step["blocker"])
            return self._save_state(state)

        previous_status = step["status"]
        if not is_import:
            step["attempts"] += 1
        step["status"] = "RUNNING"
        step["started_at"] = step["started_at"] or _now_iso()
        step["blocker"] = None
        step["error"] = None
        step["input_refs"] = [
            self.artifacts.get(key)["relative_path"]
            for key in stage.get("requires") or [] if self.artifacts.get(key)
        ]
        self.events.append("STAGE_STARTED", stage_id,
                           previous_status=previous_status, new_status="RUNNING",
                           message=f"attempt {step['attempts']}")
        self._save_state(state)

        ctx = ExecutionContext(
            project_path=self.project_path,
            root=self.root,
            project=self.project,
            stage=stage,
            pipeline=pipeline,
            state=state,
            artifacts=self.artifacts,
            costs=self.costs,
            events=self.events,
            allow_external=allow_external,
            force=force,
            imported_result=imported_result,
            imported_result_ref=imported_ref,
            bundle=self._bundle_snapshot(),
        )
        executor_name = stage["executor"]
        try:
            result = self.registry.get(executor_name)(ctx)
        except Exception as e:
            step["status"] = "FAILED"
            step["error"] = f"{type(e).__name__}: {e}"
            self.events.append("STAGE_FAILED", stage_id, new_status="FAILED",
                               message=step["error"])
            return self._save_state(state)

        # 비용 기록
        if result.cost:
            entry = self.costs.append(
                stage_id, result.cost.get("provider", "internal"),
                model_or_tool=result.cost.get("model_or_tool"),
                estimated_cost=result.cost.get("estimated_cost"),
                actual_cost=result.cost.get("actual_cost"),
                currency=result.cost.get("currency"),
                status=result.cost.get("status", "UNKNOWN"),
            )
            step["estimated_cost"] = entry["estimated_cost"]
            step["actual_cost"] = entry["actual_cost"]

        # 산출물 등록 (완료 여부와 무관하게, 생산된 파일은 인덱스에 기록)
        registered = {}
        for key, rel in (result.outputs or {}).items():
            suffix = Path(rel).suffix.lower()
            entry = self.artifacts.register(
                key, rel, producer_stage=stage_id,
                media_type=_MEDIA_TYPES.get(suffix, "application/octet-stream"),
            )
            registered[key] = rel

        if result.status == "COMPLETED":
            declared = list(stage.get("produces") or [])
            missing_outputs = [
                key for key in declared
                if key not in registered or not self.artifacts.exists(key)
            ]
            if missing_outputs:
                # executor가 선언한 output이 없으면 완료 처리하지 않는다
                step["status"] = "FAILED"
                step["error"] = f"선언된 output 미생산: {', '.join(missing_outputs)}"
                self.events.append("STAGE_FAILED", stage_id, message=step["error"])
                return self._save_state(state)
            step["status"] = "COMPLETED"
            step["completed_at"] = _now_iso()
            step["output_refs"] = registered
            self.events.append("STAGE_COMPLETED", stage_id,
                               previous_status="RUNNING", new_status="COMPLETED")
            self._advance(state, pipeline, stage)
        elif result.status in ("WAITING_INPUT", "WAITING_EXTERNAL", "WAITING_APPROVAL"):
            step["status"] = result.status
            step["output_refs"] = registered
            if result.blockers:
                step["blocker"] = "; ".join(result.blockers)
            self.events.append("STAGE_WAITING", stage_id, new_status=result.status,
                               message="; ".join(result.warnings or []))
        elif result.status == "BLOCKED":
            step["status"] = "BLOCKED"
            step["blocker"] = "; ".join(result.blockers) or "unknown"
            step["output_refs"] = registered
            self.events.append("STAGE_BLOCKED", stage_id, message=step["blocker"])
        else:  # FAILED
            step["status"] = "FAILED"
            step["error"] = "; ".join(result.blockers) or "executor 실패"
            self.events.append("STAGE_FAILED", stage_id, message=step["error"])
        return self._save_state(state)

    def _advance(self, state: dict, pipeline: dict, completed_stage: dict) -> None:
        """완료된 현재 단계 이후의 첫 미완료 단계로 이동. 없으면 COMPLETE."""
        next_stage = None
        for stage in pipeline["stages"]:
            step = state["step_states"][stage["id"]]
            if step["status"] not in ("COMPLETED", "SKIPPED"):
                next_stage = stage["id"]
                break
        state["current_stage"] = next_stage
        if completed_stage.get("kind") == "package":
            self._update_project_status("PACKAGE_READY")
        if next_stage is None:
            state["status"] = WORKFLOW_COMPLETE
            final = "COMPLETE"
            last_stage = pipeline["stages"][-1]
            if last_stage.get("kind") == "human_gate" and any(
                a["stage_id"] == last_stage["id"] and a["decision"] == "APPROVE"
                for a in state["approvals"]
            ):
                final = "APPROVED_FOR_PUBLISH"
            self._update_project_status(final)
            self.events.append("WORKFLOW_COMPLETED", message=f"최종 상태: {final}")

    def _update_project_status(self, status: str) -> None:
        project_json = self.project_path / "project.json"
        project = load_json(project_json)
        project["status"] = status
        project["updated_at"] = _now_iso()
        write_json(project_json, project)
        self.project = project

    def run_current(self, allow_external: bool = False) -> dict:
        state = self._load_state()
        if state["status"] == WORKFLOW_COMPLETE:
            return state
        pipeline = self._pipeline_snapshot()
        current = state["current_stage"]
        stage = self._stage_def(pipeline, current)
        step = state["step_states"][current]
        if step["status"] in ("WAITING_APPROVAL", "WAITING_INPUT", "WAITING_EXTERNAL"):
            # 대기 상태 — 재실행하지 않고 그대로 보고 (승인/import로만 진행)
            return state
        return self._dispatch(state, pipeline, stage, allow_external=allow_external)

    def run_until_gate(self, allow_external: bool = False, max_steps: int = 50) -> dict:
        """대기(gate/입력/외부)나 실패/차단을 만날 때까지 순차 실행한다."""
        state = self._load_state()
        for _ in range(max_steps):
            if state["status"] == WORKFLOW_COMPLETE:
                break
            current = state["current_stage"]
            step_before = state["step_states"][current]["status"]
            if step_before in ("WAITING_APPROVAL", "WAITING_INPUT", "WAITING_EXTERNAL",
                               "FAILED", "BLOCKED"):
                break
            state = self.run_current(allow_external=allow_external)
            if state["status"] == WORKFLOW_COMPLETE:
                break
            new_current = state["current_stage"]
            new_status = state["step_states"][new_current]["status"]
            if new_status in ("WAITING_APPROVAL", "WAITING_INPUT", "WAITING_EXTERNAL",
                              "FAILED", "BLOCKED"):
                break
        return state

    # --- import / 승인 / 재시도 ---
    def import_result(self, stage_id: str, result_file: str | Path,
                      allow_external: bool = False) -> dict:
        state = self._load_state()
        if state["current_stage"] != stage_id:
            raise ADOSValidationError(
                f"현재 단계({state['current_stage']})가 아닌 단계에 결과를 import할 수 없습니다: {stage_id}",
                location="ProductionWorkflowEngine.import_result",
            )
        step = state["step_states"][stage_id]
        if step["status"] not in ("WAITING_INPUT", "WAITING_EXTERNAL"):
            raise ADOSValidationError(
                f"단계가 입력 대기 상태가 아닙니다: {stage_id} ({step['status']})",
                location="ProductionWorkflowEngine.import_result",
            )
        result_file = Path(result_file)
        if not result_file.is_file():
            raise ADOSFileNotFoundError(
                f"결과 파일이 없습니다: {result_file}",
                location="ProductionWorkflowEngine.import_result",
            )
        imported = load_json(result_file)
        pipeline = self._pipeline_snapshot()
        stage = self._stage_def(pipeline, stage_id)
        self.events.append("RESULT_IMPORTED", stage_id, actor_type="human",
                           message=f"import from {result_file.name}")
        return self._dispatch(state, pipeline, stage,
                              imported_result=imported,
                              imported_ref=str(result_file),
                              allow_external=allow_external)

    def approve(self, stage_id: str, decision: str, reviewer: str = "human",
                notes: str | None = None) -> dict:
        state = self._load_state()
        if state["current_stage"] != stage_id:
            raise ADOSValidationError(
                f"현재 단계({state['current_stage']})가 아닌 단계를 승인할 수 없습니다: {stage_id}",
                location="ProductionWorkflowEngine.approve",
            )
        step = state["step_states"][stage_id]
        if step["status"] != "WAITING_APPROVAL":
            raise ADOSValidationError(
                f"승인 대기 상태가 아닙니다: {stage_id} ({step['status']})",
                location="ProductionWorkflowEngine.approve",
            )
        pipeline = self._pipeline_snapshot()
        stage = self._stage_def(pipeline, stage_id)
        allowed = (stage.get("approval") or {}).get("decisions") or [
            "APPROVE", "REQUEST_REVISION", "REJECT"
        ]
        if decision not in allowed:
            raise ADOSValidationError(
                f"허용되지 않는 결정: {decision} (허용: {', '.join(allowed)})",
                location="ProductionWorkflowEngine.approve",
            )
        record = {
            "stage_id": stage_id, "decision": decision, "reviewer": reviewer,
            "notes": notes, "timestamp": _now_iso(),
        }
        state["approvals"].append(record)
        decision_rel = APPROVALS_DIR / f"{stage_id}_decision.json"
        write_json(self.project_path / decision_rel, record)
        self.events.append("APPROVAL_RECORDED", stage_id, actor_type="human",
                           actor_id=reviewer, message=decision)

        if decision == "APPROVE":
            registered = dict(step["output_refs"] or {})
            for key in stage.get("produces") or []:
                if key not in registered:
                    rel = str(decision_rel).replace("\\", "/")
                    self.artifacts.register(key, rel, producer_stage=stage_id,
                                            media_type="application/json")
                    registered[key] = rel
            step["output_refs"] = registered
            step["status"] = "COMPLETED"
            step["completed_at"] = _now_iso()
            self.events.append("STAGE_COMPLETED", stage_id,
                               previous_status="WAITING_APPROVAL", new_status="COMPLETED")
            self._advance(state, pipeline, stage)
        elif decision == "REQUEST_REVISION":
            step["status"] = "PENDING"
            step["blocker"] = f"REQUEST_REVISION by {reviewer}: {notes or ''}"
            state["blockers"].append({"stage_id": stage_id, "type": "REVISION_REQUESTED",
                                      "notes": notes, "timestamp": _now_iso()})
        else:  # REJECT
            step["status"] = "FAILED"
            step["error"] = f"REJECTED by {reviewer}: {notes or ''}"
            state["status"] = WORKFLOW_BLOCKED
            state["blockers"].append({"stage_id": stage_id, "type": "REJECTED",
                                      "notes": notes, "timestamp": _now_iso()})
        return self._save_state(state)

    def retry(self, stage_id: str, force: bool = False,
              allow_external: bool = False) -> dict:
        state = self._load_state()
        pipeline = self._pipeline_snapshot()
        stage = self._stage_def(pipeline, stage_id)
        step = state["step_states"][stage_id]

        if force:
            # --force: 완료된 단계 포함 특정 단계 재실행
            step["status"] = "PENDING"
            step["attempts"] = 0
            step["error"] = None
            step["blocker"] = None
            state["current_stage"] = stage_id
            if state["status"] == WORKFLOW_COMPLETE:
                state["status"] = WORKFLOW_RUNNING
            self._save_state(state)
            self.events.append("STAGE_FORCE_RERUN", stage_id, actor_type="human")
            return self._dispatch(self._load_state(), pipeline, stage,
                                  allow_external=allow_external, force=True)

        if state["current_stage"] != stage_id:
            raise ADOSValidationError(
                f"현재 단계({state['current_stage']})가 아닌 단계는 --force 없이 재실행할 수 없습니다: {stage_id}",
                location="ProductionWorkflowEngine.retry",
            )
        if step["status"] not in ("FAILED", "BLOCKED", "PENDING"):
            raise ADOSValidationError(
                f"재시도 대상 상태가 아닙니다: {stage_id} ({step['status']})",
                location="ProductionWorkflowEngine.retry",
                suggested_fix="완료된 단계 재실행은 --force를 사용하세요.",
            )
        step["status"] = "PENDING"
        step["error"] = None
        step["blocker"] = None
        self._save_state(state)
        return self._dispatch(self._load_state(), pipeline, stage,
                              allow_external=allow_external)
