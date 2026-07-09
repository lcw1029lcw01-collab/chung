# -*- coding: utf-8 -*-
"""Editing engine (walking skeleton).

모든 상위 계획(타임라인/비주얼/모션/음성/자막)을 참조하는 더미 편집 계획을 만든다.
전체 스키마는 docs/25_EDITING_ENGINE.md 기준으로 이후 확장한다.

주의: 영상을 조립하지 않는다. ffmpeg를 호출하지 않는다. mp4를 만들지 않는다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSValidator,
    load_json,
    write_json,
)

EDIT_DIR = "edit"
PLAN_FILE = "editing_plan.json"

REQUIRED_INPUTS = {
    "timeline_ref": ("timeline/timeline.json", "TimelineEngine.create_dummy_timeline"),
    "visual_plan_ref": ("assets/images/visual_plan.json", "VisualEngine.create_dummy_visual_plan"),
    "motion_plan_ref": ("assets/motion/motion_plan.json", "MotionEngine.create_dummy_motion_plan"),
    "voice_plan_ref": ("assets/audio/voice_plan.json", "VoiceEngine.create_dummy_voice_plan"),
    "subtitle_plan_ref": ("assets/subtitles/subtitle_plan.json", "SubtitleEngine.create_dummy_subtitle_plan"),
}

PLAN_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "editing_mode",
    "production_ready",
    "disclaimer",
    "timeline_ref",
    "visual_plan_ref",
    "motion_plan_ref",
    "voice_plan_ref",
    "subtitle_plan_ref",
    "assembly_steps",
    "estimated_duration_seconds",
    "created_at",
]

ASSEMBLY_STEP_REQUIRED_FIELDS = [
    "step_id",
    "order",
    "step_type",
    "description",
    "status",
]

DUMMY_DISCLAIMER = "Dummy editing plan. No real video assembled."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EditingEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def plan_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / EDIT_DIR / PLAN_FILE

    def create_dummy_editing_plan(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for ref_key, (rel, fix) in REQUIRED_INPUTS.items():
            if not (project_path / rel).is_file():
                raise ADOSFileNotFoundError(
                    f"{rel}가 없습니다: {project_path / rel}",
                    location="EditingEngine.create_dummy_editing_plan",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        timeline = load_json(project_path / "timeline" / "timeline.json")
        # 상위 계획들 존재+파싱 검증
        for rel, _ in REQUIRED_INPUTS.values():
            load_json(project_path / rel)

        step_defs = [
            ("load_timeline", "타임라인을 불러와 편집 기준으로 설정한다."),
            ("place_images", "장면별 이미지 자산을 타임라인에 배치한다."),
            ("apply_motion", "모션 클립을 해당 장면에 적용한다."),
            ("add_voice", "나레이션 오디오 트랙을 배치한다."),
            ("add_subtitles", "언어별 자막 트랙을 배치한다."),
            ("render_preview", "프리뷰 렌더 설정을 준비한다 (실제 렌더 없음)."),
        ]
        assembly_steps = [
            {
                "step_id": f"ST{i:03d}",
                "order": i,
                "step_type": step_type,
                "description": f"{description} (placeholder)",
                "status": "PLANNED",
            }
            for i, (step_type, description) in enumerate(step_defs, start=1)
        ]

        plan = {
            "project_id": project["project_id"],
            "topic": topic["title"],
            "editing_mode": "dummy",
            "production_ready": False,
            "disclaimer": DUMMY_DISCLAIMER,
            "timeline_ref": REQUIRED_INPUTS["timeline_ref"][0],
            "visual_plan_ref": REQUIRED_INPUTS["visual_plan_ref"][0],
            "motion_plan_ref": REQUIRED_INPUTS["motion_plan_ref"][0],
            "voice_plan_ref": REQUIRED_INPUTS["voice_plan_ref"][0],
            "subtitle_plan_ref": REQUIRED_INPUTS["subtitle_plan_ref"][0],
            "assembly_steps": assembly_steps,
            "estimated_duration_seconds": int(timeline["total_duration_seconds"]),
            "created_at": _now_iso(),
        }
        folder = project_path / EDIT_DIR
        write_json(folder / PLAN_FILE, plan)
        write_json(
            folder / "assembly_manifest.json",
            {
                "project_id": project["project_id"],
                "editing_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "inputs": {k: v[0] for k, v in REQUIRED_INPUTS.items()},
                "outputs": [],  # 실제 영상 파일은 만들지 않는다
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "editing_review.json",
            {
                "project_id": project["project_id"],
                "editing_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 편집 계획 — 실제 편집 검토는 Quality 단계 구현 후 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 편집 계획 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"], "steps": len(assembly_steps)},
            )
        return plan

    def load_editing_plan(self, project_path: str | Path) -> dict:
        path = self.plan_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"editing_plan.json이 없습니다: {path}",
                location="EditingEngine.load_editing_plan",
                suggested_fix="create_dummy_editing_plan을 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_editing_plan(self, project_path: str | Path) -> bool:
        plan = self.load_editing_plan(project_path)
        loc = "EditingEngine.validate_editing_plan"
        ADOSValidator.require_fields(plan, PLAN_REQUIRED_FIELDS, location=loc)
        for step in plan["assembly_steps"]:
            ADOSValidator.require_fields(step, ASSEMBLY_STEP_REQUIRED_FIELDS, location=loc)
        return True
