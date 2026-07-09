# -*- coding: utf-8 -*-
"""ADOS Direction → Timeline → Visual walking skeleton 데모.

단계별(stage-specific) 디버깅용 데모다.
전체 파이프라인은 scripts/run_full_dummy_pipeline.py를 사용한다.

앞 단계(R→K→S)는 기존 데모 로직을 재사용해 DIRECTION까지 진행한 뒤,
DIRECTION → TIMELINE → VISUAL 더미 산출물을 만들고 MOTION 단계로 전환한다.

실행: 프로젝트 루트에서  python scripts/run_direction_timeline_visual_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from core import ADOSPathManager, StageName  # noqa: E402
from engines.direction import DirectionEngine  # noqa: E402
from engines.timeline import TimelineEngine  # noqa: E402
from engines.visual import VisualEngine  # noqa: E402
from engines.workflow import WorkflowOrchestrator  # noqa: E402
from run_research_knowledge_story_demo import (  # noqa: E402
    run_research_knowledge_story_demo,
)


def run_direction_timeline_visual_demo(
    path_manager: ADOSPathManager | None = None,
) -> dict:
    pm = path_manager or ADOSPathManager()

    # R→K→S 완료 후 current_stage = DIRECTION 상태로 시작
    upstream = run_research_knowledge_story_demo(pm)
    project_path = Path(upstream["project_path"])
    orchestrator = WorkflowOrchestrator()

    direction = DirectionEngine()
    direction.create_dummy_direction(project_path)
    orchestrator.write_stage_result(
        project_path, str(StageName.DIRECTION),
        {"direction_plan_ref": "direction/direction_plan.json", "mode": "dummy"},
    )
    orchestrator.mark_stage_completed(
        project_path, str(StageName.DIRECTION),
        result_ref="direction/direction_plan.json",
    )
    orchestrator.advance_to_next_stage(project_path)  # → TIMELINE

    timeline = TimelineEngine()
    timeline.create_dummy_timeline(project_path)
    orchestrator.write_stage_result(
        project_path, str(StageName.TIMELINE),
        {"timeline_ref": "timeline/timeline.json", "mode": "dummy"},
    )
    orchestrator.mark_stage_completed(
        project_path, str(StageName.TIMELINE), result_ref="timeline/timeline.json"
    )
    orchestrator.advance_to_next_stage(project_path)  # → VISUAL

    visual = VisualEngine()
    visual.create_dummy_visual_plan(project_path)
    orchestrator.write_stage_result(
        project_path, str(StageName.VISUAL),
        {"visual_plan_ref": "assets/images/visual_plan.json", "mode": "dummy"},
    )
    orchestrator.mark_stage_completed(
        project_path, str(StageName.VISUAL),
        result_ref="assets/images/visual_plan.json",
    )
    current_stage = orchestrator.advance_to_next_stage(project_path)  # → MOTION

    return {
        "project_id": upstream["project_id"],
        "project_path": str(project_path),
        "direction_plan_path": str(direction.plan_path(project_path)),
        "timeline_path": str(timeline.timeline_path(project_path)),
        "visual_plan_path": str(visual.plan_path(project_path)),
        "current_stage": current_stage,
    }


def main() -> int:
    result = run_direction_timeline_visual_demo()
    print(f"project_id          : {result['project_id']}")
    print(f"project path        : {result['project_path']}")
    print(f"direction_plan path : {result['direction_plan_path']}")
    print(f"timeline path       : {result['timeline_path']}")
    print(f"visual_plan path    : {result['visual_plan_path']}")
    print(f"current_stage       : {result['current_stage']} (VISUAL 완료 후)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
