# -*- coding: utf-8 -*-
"""Visual engine (walking skeleton).

타임라인과 연출 계획을 기반으로 더미 비주얼 계획을 만든다.
전체 스키마는 docs/21_VISUAL_ENGINE.md 기준으로 이후 확장한다.

주의: Midjourney를 호출하지 않는다. 이미지 파일을 만들지 않는다.
JSON 계획/placeholder만 생성한다.
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

PROMPTS_DIR = "prompts"
IMAGES_DIR = Path("assets") / "images"
PLAN_FILE = "visual_plan.json"

PLAN_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "visual_mode",
    "total_scenes",
    "visual_style",
    "scene_visuals",
    "provider_hint",
    "production_ready",
    "disclaimer",
    "created_at",
]

SCENE_VISUAL_REQUIRED_FIELDS = [
    "scene_id",
    "order",
    "purpose",
    "prompt_mode",
    "image_prompt",
    "required_image_count",
    "status",
]

DUMMY_DISCLAIMER = "Dummy visual plan. No real images generated."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class VisualEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def plan_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / IMAGES_DIR / PLAN_FILE

    def create_dummy_visual_plan(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for required, fix in (
            ("timeline/timeline.json", "TimelineEngine.create_dummy_timeline"),
            ("direction/direction_plan.json", "DirectionEngine.create_dummy_direction"),
        ):
            if not (project_path / required).is_file():
                raise ADOSFileNotFoundError(
                    f"{required}가 없습니다: {project_path / required}",
                    location="VisualEngine.create_dummy_visual_plan",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        timeline = load_json(project_path / "timeline" / "timeline.json")
        direction = load_json(project_path / "direction" / "direction_plan.json")

        title = topic["title"]
        visual_style = direction["visual_style"]
        scene_visuals = []
        for scene in timeline["scenes"]:
            if not scene["visual"]["required"]:
                continue
            scene_visuals.append(
                {
                    "scene_id": scene["scene_id"],
                    "order": scene["order"],
                    "purpose": scene["purpose"],
                    "prompt_mode": "dummy",
                    "image_prompt": (
                        f"{visual_style}, {scene['purpose']} scene for '{title}' "
                        "(placeholder prompt, do not use in production)"
                    ),
                    "required_image_count": 1,
                    "status": "PLANNED",
                }
            )

        plan = {
            "project_id": project["project_id"],
            "topic": title,
            "visual_mode": "dummy",
            "total_scenes": len(scene_visuals),
            "visual_style": visual_style,
            "scene_visuals": scene_visuals,
            "provider_hint": "midjourney",
            "production_ready": False,
            "disclaimer": DUMMY_DISCLAIMER,
            "created_at": _now_iso(),
        }

        write_json(
            project_path / PROMPTS_DIR / "visual_prompts.json",
            {
                "project_id": project["project_id"],
                "visual_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "prompts": [
                    {"scene_id": sv["scene_id"], "prompt": sv["image_prompt"]}
                    for sv in scene_visuals
                ],
                "created_at": _now_iso(),
            },
        )
        images_folder = project_path / IMAGES_DIR
        write_json(
            images_folder / "image_manifest.json",
            {
                "project_id": project["project_id"],
                "visual_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "images": [],  # 실제 이미지는 생성하지 않는다
                "expected_images": [
                    {
                        "scene_id": sv["scene_id"],
                        "count": sv["required_image_count"],
                        "status": "PLANNED",
                    }
                    for sv in scene_visuals
                ],
                "created_at": _now_iso(),
            },
        )
        write_json(images_folder / PLAN_FILE, plan)
        write_json(
            images_folder / "visual_review.json",
            {
                "project_id": project["project_id"],
                "visual_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 비주얼 계획 — 실제 이미지 검토는 이후 단계에서 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 비주얼 계획 생성: {project['project_id']}",
                metadata={
                    "project_id": project["project_id"],
                    "scenes": len(scene_visuals),
                },
            )
        return plan

    def load_visual_plan(self, project_path: str | Path) -> dict:
        path = self.plan_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"visual_plan.json이 없습니다: {path}",
                location="VisualEngine.load_visual_plan",
                suggested_fix="create_dummy_visual_plan을 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_visual_plan(self, project_path: str | Path) -> bool:
        plan = self.load_visual_plan(project_path)
        loc = "VisualEngine.validate_visual_plan"
        ADOSValidator.require_fields(plan, PLAN_REQUIRED_FIELDS, location=loc)
        for sv in plan["scene_visuals"]:
            ADOSValidator.require_fields(sv, SCENE_VISUAL_REQUIRED_FIELDS, location=loc)
        return True
