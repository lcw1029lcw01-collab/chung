# -*- coding: utf-8 -*-
"""Workflow state manager (walking skeleton).

workflow/workflow_state.json을 생성·로드·갱신한다.
전체 스키마는 docs/15_WORKFLOW_ORCHESTRATOR.md 기준으로 이후 확장한다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSValidationError,
    ADOSValidator,
    StageName,
    load_json,
    write_json,
)

STATE_RELATIVE_PATH = Path("workflow") / "workflow_state.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkflowStateManager:
    @staticmethod
    def state_path(project_path: str | Path) -> Path:
        return Path(project_path) / STATE_RELATIVE_PATH

    @classmethod
    def create_workflow_state(cls, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project_json = project_path / "project.json"
        if not project_json.is_file():
            raise ADOSFileNotFoundError(
                f"project.json이 없습니다: {project_path}",
                location="WorkflowStateManager.create_workflow_state",
                suggested_fix="ProjectEngine.create_project로 프로젝트를 먼저 생성하세요.",
            )
        state_file = cls.state_path(project_path)
        if state_file.is_file():
            raise ADOSValidationError(
                f"workflow_state.json이 이미 존재합니다: {state_file}",
                location="WorkflowStateManager.create_workflow_state",
                suggested_fix="기존 workflow 상태를 사용하세요.",
            )
        project = load_json(project_json)
        now = _now_iso()
        state = {
            "project_id": project["project_id"],
            "status": "RUNNING",
            "current_stage": str(StageName.INITIALIZED),
            "completed_stages": [],
            "stage_history": [],
            "created_at": now,
            "updated_at": now,
        }
        write_json(state_file, state)
        return state

    @classmethod
    def load_workflow_state(cls, project_path: str | Path) -> dict:
        state_file = cls.state_path(project_path)
        if not state_file.is_file():
            raise ADOSFileNotFoundError(
                f"workflow_state.json이 없습니다: {state_file}",
                location="WorkflowStateManager.load_workflow_state",
                suggested_fix="WorkflowOrchestrator.initialize_workflow를 먼저 실행하세요.",
            )
        return load_json(state_file)

    @classmethod
    def save_workflow_state(cls, project_path: str | Path, state: dict) -> dict:
        state["updated_at"] = _now_iso()
        write_json(cls.state_path(project_path), state)
        return state

    @classmethod
    def get_current_stage(cls, project_path: str | Path) -> str:
        return cls.load_workflow_state(project_path)["current_stage"]

    @classmethod
    def set_current_stage(cls, project_path: str | Path, stage: str) -> dict:
        ADOSValidator.validate_enum(
            stage, StageName, field="stage",
            location="WorkflowStateManager.set_current_stage",
        )
        state = cls.load_workflow_state(project_path)
        state["current_stage"] = str(stage)
        return cls.save_workflow_state(project_path, state)

    @classmethod
    def append_stage_history(
        cls, project_path: str | Path, stage: str, status: str, notes: str | None = None
    ) -> dict:
        ADOSValidator.validate_enum(
            stage, StageName, field="stage",
            location="WorkflowStateManager.append_stage_history",
        )
        state = cls.load_workflow_state(project_path)
        state["stage_history"].append(
            {
                "stage": str(stage),
                "status": status,
                "notes": notes,
                "timestamp": _now_iso(),
            }
        )
        return cls.save_workflow_state(project_path, state)
