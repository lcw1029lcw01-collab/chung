# -*- coding: utf-8 -*-
"""Project view builder — render-neutral view model(ui/project_view.json) 생성.

템플릿의 project_view 설정(탭·카드·KPI)과 런타임 상태(workflow/approvals/
artifacts/provider jobs/costs/blockers)를 합친다. 템플릿에 따라 탭이 달라지며,
Python 코드에 특정 콘텐츠 전용 탭을 하드코딩하지 않는다.
향후 하나의 공통 프론트엔드가 이 파일 하나만 읽으면 되도록 만든다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import load_json, write_json

from .artifact_index import ArtifactIndex
from .runtime_records import CostLedger

VIEW_REL = Path("ui") / "project_view.json"

_WAITING_ACTIONS = {
    "WAITING_APPROVAL": "APPROVE",
    "WAITING_INPUT": "IMPORT_RESULT",
    "WAITING_EXTERNAL": "IMPORT_RESULT",
    "FAILED": "RETRY",
    "BLOCKED": "RETRY",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProjectViewBuilder:
    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path)

    def _load_optional(self, rel: str) -> dict | None:
        path = self.project_path / rel
        return load_json(path) if path.is_file() else None

    def build(self) -> dict:
        project = self._load_optional("project.json") or {}
        state = self._load_optional("workflow/workflow_state.json") or {}
        bundle = self._load_optional("workflow/template_bundle_snapshot.json") or {}
        pipeline_ref = state.get("pipeline_snapshot_ref")
        pipeline = self._load_optional(pipeline_ref) if pipeline_ref else None
        view_config = bundle.get("project_view") or {}
        artifacts = ArtifactIndex(self.project_path).all()
        costs = CostLedger(self.project_path).summary()
        provider_queue = self._load_optional("providers/job_queue.json") or {}

        step_states = state.get("step_states") or {}
        stages_summary = []
        for stage in (pipeline or {}).get("stages") or []:
            step = step_states.get(stage["id"], {})
            stages_summary.append({
                "id": stage["id"],
                "title": stage.get("title"),
                "kind": stage.get("kind"),
                "owner_role": stage.get("owner_role"),
                "status": step.get("status"),
                "attempts": step.get("attempts"),
                "blocker": step.get("blocker"),
                "error": step.get("error"),
            })
        stage_by_id = {s["id"]: s for s in stages_summary}
        completed = sum(1 for s in stages_summary if s["status"] == "COMPLETED")
        total = len(stages_summary)

        tabs = []
        for tab in view_config.get("tabs") or []:
            tabs.append({
                "id": tab.get("id"),
                "title": tab.get("title"),
                "cards": tab.get("cards") or [],
                "stages": [stage_by_id.get(sid, {"id": sid}) for sid in tab.get("stages") or []],
                "artifacts": [
                    artifacts.get(key, {"artifact_key": key, "status": "MISSING"})
                    for key in tab.get("artifacts") or []
                ],
            })

        # KPI 해석 (템플릿 설정 기반)
        kpis = []
        for kpi in view_config.get("kpis") or []:
            kpis.append({
                "key": kpi.get("key"), "label": kpi.get("label"),
                "value": self._resolve_kpi(kpi.get("source"), project, artifacts, costs),
            })

        next_action = self._next_action(state)
        blockers = list(state.get("blockers") or [])
        for stage in stages_summary:
            if stage["blocker"]:
                blockers.append({"stage_id": stage["id"], "type": "STEP_BLOCKER",
                                 "notes": stage["blocker"]})

        view = {
            "view_id": view_config.get("view_id", "default"),
            "project": {
                "project_id": project.get("project_id"),
                "name": project.get("project_name"),
                "status": project.get("status"),
                "channel": project.get("channel"),
                "content_type": project.get("content_type"),
                "run_mode": project.get("run_mode"),
                "project_inputs": project.get("project_inputs"),
            },
            "template": {
                "template_id": state.get("template_id") or project.get("template_id"),
                "template_version": state.get("template_version"),
                "pipeline_id": state.get("pipeline_id"),
                "pipeline_version": state.get("pipeline_version"),
            },
            "workflow": {
                "status": state.get("status"),
                "current_stage": state.get("current_stage"),
                "progress": {
                    "completed": completed, "total": total,
                    "percent": round(completed * 100 / total) if total else 0,
                },
            },
            "tabs": tabs,
            "stages": stages_summary,
            "approvals": state.get("approvals") or [],
            "artifacts": artifacts,
            "provider_jobs": provider_queue.get("jobs") or [],
            "blockers": blockers,
            "costs": costs,
            "kpis": kpis,
            "next_action": next_action,
            "updated_at": _now_iso(),
        }
        write_json(self.project_path / VIEW_REL, view)
        return view

    @staticmethod
    def _resolve_kpi(source: str | None, project: dict, artifacts: dict, costs: dict):
        if not source:
            return None
        if source.startswith("project_inputs."):
            return (project.get("project_inputs") or {}).get(source.split(".", 1)[1])
        if source.startswith("artifact_metadata."):
            _, key, field = source.split(".", 2)
            return ((artifacts.get(key) or {}).get("metadata") or {}).get(field)
        if source.startswith("costs."):
            return costs.get(source.split(".", 1)[1])
        return None

    @staticmethod
    def _next_action(state: dict) -> dict:
        if not state:
            return {"action": "NONE", "description": "workflow 없음"}
        if state.get("status") == "COMPLETE":
            return {"action": "NONE", "description": "workflow 완료"}
        current = state.get("current_stage")
        if not current:
            return {"action": "NONE", "description": "실행할 단계 없음"}
        step = (state.get("step_states") or {}).get(current) or {}
        action = _WAITING_ACTIONS.get(step.get("status"), "RUN")
        return {"action": action, "stage": current,
                "description": f"{current}: {step.get('status', 'PENDING')}"}
