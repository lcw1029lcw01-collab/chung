# -*- coding: utf-8 -*-
"""Motion engine (walking skeleton).

비주얼 계획과 타임라인을 기반으로 더미 모션 계획을 만든다.
전체 스키마는 docs/22_MOTION_ENGINE.md 기준으로 이후 확장한다.

주의: Midjourney Video를 호출하지 않는다. 영상 파일을 만들지 않는다.
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

MOTION_DIR = Path("assets") / "motion"
PLAN_FILE = "motion_plan.json"

PLAN_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "motion_mode",
    "total_scenes",
    "provider_hint",
    "production_ready",
    "disclaimer",
    "scene_motions",
    "created_at",
]

SCENE_MOTION_REQUIRED_FIELDS = [
    "scene_id",
    "order",
    "motion_prompt",
    "duration_seconds",
    "status",
]

DUMMY_DISCLAIMER = "Dummy motion plan. No real video generated."

# 더미 모션 클립의 최대 길이 (초)
_MAX_MOTION_SECONDS = 5


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MotionEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def plan_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / MOTION_DIR / PLAN_FILE

    def create_dummy_motion_plan(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for required, fix in (
            ("assets/images/visual_plan.json", "VisualEngine.create_dummy_visual_plan"),
            ("timeline/timeline.json", "TimelineEngine.create_dummy_timeline"),
        ):
            if not (project_path / required).is_file():
                raise ADOSFileNotFoundError(
                    f"{required}가 없습니다: {project_path / required}",
                    location="MotionEngine.create_dummy_motion_plan",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        timeline = load_json(project_path / "timeline" / "timeline.json")
        visual_plan = load_json(project_path / "assets" / "images" / "visual_plan.json")

        prompts_by_scene = {
            sv["scene_id"]: sv["image_prompt"] for sv in visual_plan["scene_visuals"]
        }
        title = topic["title"]
        scene_motions = []
        for scene in timeline["scenes"]:
            if not scene["motion"]["required"]:
                continue
            base_prompt = prompts_by_scene.get(
                scene["scene_id"], f"scene for '{title}'"
            )
            scene_motions.append(
                {
                    "scene_id": scene["scene_id"],
                    "order": scene["order"],
                    "motion_prompt": (
                        f"{base_prompt} — subtle cinematic camera motion "
                        "(placeholder, do not use in production)"
                    ),
                    "duration_seconds": min(_MAX_MOTION_SECONDS, scene["duration_seconds"]),
                    "status": "PLANNED",
                }
            )

        plan = {
            "project_id": project["project_id"],
            "topic": title,
            "motion_mode": "dummy",
            "total_scenes": len(scene_motions),
            "provider_hint": "midjourney_video",
            "production_ready": False,
            "disclaimer": DUMMY_DISCLAIMER,
            "scene_motions": scene_motions,
            "created_at": _now_iso(),
        }
        folder = project_path / MOTION_DIR
        write_json(folder / PLAN_FILE, plan)
        write_json(
            folder / "motion_manifest.json",
            {
                "project_id": project["project_id"],
                "motion_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "clips": [],  # 실제 영상 클립은 생성하지 않는다
                "expected_clips": [
                    {"scene_id": sm["scene_id"], "status": "PLANNED"}
                    for sm in scene_motions
                ],
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "motion_review.json",
            {
                "project_id": project["project_id"],
                "motion_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 모션 계획 — 실제 클립 검토는 이후 단계에서 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 모션 계획 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"], "scenes": len(scene_motions)},
            )
        return plan

    def load_motion_plan(self, project_path: str | Path) -> dict:
        path = self.plan_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"motion_plan.json이 없습니다: {path}",
                location="MotionEngine.load_motion_plan",
                suggested_fix="create_dummy_motion_plan을 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_motion_plan(self, project_path: str | Path) -> bool:
        plan = self.load_motion_plan(project_path)
        loc = "MotionEngine.validate_motion_plan"
        ADOSValidator.require_fields(plan, PLAN_REQUIRED_FIELDS, location=loc)
        for sm in plan["scene_motions"]:
            ADOSValidator.require_fields(sm, SCENE_MOTION_REQUIRED_FIELDS, location=loc)
        return True
