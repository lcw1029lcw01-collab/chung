# -*- coding: utf-8 -*-
"""ADOS Motion → Voice → Subtitle → Editing walking skeleton 데모.

앞 단계(R→K→S→D→T→V)는 기존 데모 로직을 재사용해 MOTION까지 진행한 뒤,
MOTION → VOICE → SUBTITLE → EDITING 더미 계획을 만들고 QUALITY 단계로 전환한다.

실행: 프로젝트 루트에서  python scripts/run_motion_voice_subtitle_editing_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from core import ADOSPathManager, StageName  # noqa: E402
from engines.editing import EditingEngine  # noqa: E402
from engines.motion import MotionEngine  # noqa: E402
from engines.subtitle import SubtitleEngine  # noqa: E402
from engines.voice import VoiceEngine  # noqa: E402
from engines.workflow import WorkflowOrchestrator  # noqa: E402
from run_direction_timeline_visual_demo import (  # noqa: E402
    run_direction_timeline_visual_demo,
)


def run_motion_voice_subtitle_editing_demo(
    path_manager: ADOSPathManager | None = None,
) -> dict:
    pm = path_manager or ADOSPathManager()

    # R→K→S→D→T→V 완료 후 current_stage = MOTION 상태로 시작
    upstream = run_direction_timeline_visual_demo(pm)
    project_path = Path(upstream["project_path"])
    orchestrator = WorkflowOrchestrator()

    motion = MotionEngine()
    voice = VoiceEngine()
    subtitle = SubtitleEngine()
    editing = EditingEngine()

    stages = [
        (StageName.MOTION, motion.create_dummy_motion_plan, "assets/motion/motion_plan.json"),
        (StageName.VOICE, voice.create_dummy_voice_plan, "assets/audio/voice_plan.json"),
        (StageName.SUBTITLE, subtitle.create_dummy_subtitle_plan, "assets/subtitles/subtitle_plan.json"),
        (StageName.EDITING, editing.create_dummy_editing_plan, "edit/editing_plan.json"),
    ]
    current_stage = None
    for stage, run, ref in stages:
        run(project_path)
        orchestrator.write_stage_result(
            project_path, str(stage), {"plan_ref": ref, "mode": "dummy"}
        )
        orchestrator.mark_stage_completed(project_path, str(stage), result_ref=ref)
        current_stage = orchestrator.advance_to_next_stage(project_path)

    return {
        "project_id": upstream["project_id"],
        "project_path": str(project_path),
        "motion_plan_path": str(motion.plan_path(project_path)),
        "voice_plan_path": str(voice.plan_path(project_path)),
        "subtitle_plan_path": str(subtitle.plan_path(project_path)),
        "editing_plan_path": str(editing.plan_path(project_path)),
        "current_stage": current_stage,
    }


def main() -> int:
    result = run_motion_voice_subtitle_editing_demo()
    print(f"project_id         : {result['project_id']}")
    print(f"project path       : {result['project_path']}")
    print(f"motion_plan path   : {result['motion_plan_path']}")
    print(f"voice_plan path    : {result['voice_plan_path']}")
    print(f"subtitle_plan path : {result['subtitle_plan_path']}")
    print(f"editing_plan path  : {result['editing_plan_path']}")
    print(f"current_stage      : {result['current_stage']} (EDITING 완료 후)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
