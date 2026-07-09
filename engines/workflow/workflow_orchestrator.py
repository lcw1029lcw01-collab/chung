# -*- coding: utf-8 -*-
"""Workflow orchestrator (walking skeleton).

실제 엔진은 실행하지 않고 Stage 상태 전환만 안전하게 관리한다.
Stage 순서는 core.types.STAGE_ORDER (docs/15_WORKFLOW_ORCHESTRATOR.md #5).
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSLogger,
    ADOSValidationError,
    ADOSValidator,
    STAGE_ORDER,
    StageName,
    write_json,
)

from .workflow_state_manager import WorkflowStateManager

STAGE_RESULTS_DIR = Path("workflow") / "stage_results"


class WorkflowOrchestrator:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger
        self.state = WorkflowStateManager

    def initialize_workflow(self, project_path: str | Path) -> dict:
        state = self.state.create_workflow_state(project_path)
        if self.logger:
            self.logger.info(
                f"workflow 초기화: {state['project_id']}",
                metadata={"project_id": state["project_id"]},
            )
        return state

    def mark_stage_completed(
        self, project_path: str | Path, stage: str, result_ref: str | None = None
    ) -> dict:
        ADOSValidator.validate_enum(
            stage, StageName, field="stage",
            location="WorkflowOrchestrator.mark_stage_completed",
        )
        state = self.state.load_workflow_state(project_path)
        if str(stage) not in state["completed_stages"]:
            state["completed_stages"].append(str(stage))
        self.state.save_workflow_state(project_path, state)
        self.state.append_stage_history(
            project_path, stage, "COMPLETED", notes=result_ref
        )
        if self.logger:
            self.logger.info(
                f"stage 완료: {stage}",
                metadata={"project_id": state["project_id"], "stage": str(stage)},
            )
        return self.state.load_workflow_state(project_path)

    def advance_to_next_stage(self, project_path: str | Path) -> str:
        current = self.state.get_current_stage(project_path)
        try:
            index = STAGE_ORDER.index(StageName(current))
        except ValueError as e:
            raise ADOSValidationError(
                f"알 수 없는 current_stage: {current}",
                location="WorkflowOrchestrator.advance_to_next_stage",
            ) from e
        if index + 1 >= len(STAGE_ORDER):
            raise ADOSValidationError(
                f"마지막 단계입니다. 더 진행할 수 없습니다: {current}",
                location="WorkflowOrchestrator.advance_to_next_stage",
            )
        next_stage = str(STAGE_ORDER[index + 1])
        self.state.set_current_stage(project_path, next_stage)
        return next_stage

    def write_stage_result(
        self, project_path: str | Path, stage: str, result: dict
    ) -> Path:
        ADOSValidator.validate_enum(
            stage, StageName, field="stage",
            location="WorkflowOrchestrator.write_stage_result",
        )
        path = Path(project_path) / STAGE_RESULTS_DIR / f"{stage}_result.json"
        write_json(
            path,
            {
                "stage": str(stage),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "result": result,
            },
        )
        return path
