# -*- coding: utf-8 -*-
"""ADOS workflow + timeline walking skeleton 데모.

흐름: 채널 준비 → 프로젝트 생성 → workflow 초기화 → 더미 타임라인 생성
      → TIMELINE stage 결과 기록·완료 → 다음 단계로 전환

실행: 프로젝트 루트에서  python scripts/run_workflow_timeline_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from core import ADOSPathManager, StageName  # noqa: E402
from engines.timeline import TimelineEngine  # noqa: E402
from engines.workflow import WorkflowOrchestrator, WorkflowStateManager  # noqa: E402
from create_sample_channel import channel_exists, create_sample_channel  # noqa: E402
from create_sample_project import create_sample_project  # noqa: E402


def run_workflow_timeline_demo(path_manager: ADOSPathManager | None = None) -> dict:
    pm = path_manager or ADOSPathManager()

    if not channel_exists(pm):
        create_sample_channel(pm)

    project = create_sample_project(pm)
    project_path = Path(project["path"])

    orchestrator = WorkflowOrchestrator()
    orchestrator.initialize_workflow(project_path)

    # 데모: TIMELINE 단계로 이동해 더미 타임라인을 만들고 완료 처리
    WorkflowStateManager.set_current_stage(project_path, str(StageName.TIMELINE))
    TimelineEngine().create_dummy_timeline(project_path)
    orchestrator.write_stage_result(
        project_path,
        str(StageName.TIMELINE),
        {"timeline_ref": "timeline/timeline.json", "scenes": 3},
    )
    orchestrator.mark_stage_completed(
        project_path, str(StageName.TIMELINE), result_ref="timeline/timeline.json"
    )
    current_stage = orchestrator.advance_to_next_stage(project_path)

    return {
        "project_id": project["project_id"],
        "project_path": str(project_path),
        "workflow_state_path": str(WorkflowStateManager.state_path(project_path)),
        "timeline_path": str(TimelineEngine().timeline_path(project_path)),
        "current_stage": current_stage,
    }


def main() -> int:
    result = run_workflow_timeline_demo()
    print(f"project_id          : {result['project_id']}")
    print(f"project path        : {result['project_path']}")
    print(f"workflow_state path : {result['workflow_state_path']}")
    print(f"timeline path       : {result['timeline_path']}")
    print(f"current_stage       : {result['current_stage']} (TIMELINE 완료 후)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
