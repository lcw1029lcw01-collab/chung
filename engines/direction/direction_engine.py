# -*- coding: utf-8 -*-
"""Direction engine (walking skeleton).

더미 스토리를 기반으로 더미 연출 계획을 만든다.
전체 스키마는 docs/20_DIRECTION_ENGINE.md 기준으로 이후 확장한다.

주의: 최종 크리에이티브 디렉션이 아니다. 모든 출력은 dummy/placeholder이다.
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

DIRECTION_DIR = "direction"
PLAN_FILE = "direction_plan.json"

PLAN_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "direction_mode",
    "visual_style",
    "tone",
    "pacing",
    "scene_direction_rules",
    "narration_direction",
    "visual_prompt_rules",
    "risk_notes",
    "created_at",
    "disclaimer",
]

DUMMY_DISCLAIMER = "Dummy direction plan. Not production-ready."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DirectionEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def plan_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / DIRECTION_DIR / PLAN_FILE

    def create_dummy_direction(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for required in ("story/story_outline.json", "story/script_draft.json"):
            if not (project_path / required).is_file():
                raise ADOSFileNotFoundError(
                    f"{required}가 없습니다: {project_path / required}",
                    location="DirectionEngine.create_dummy_direction",
                    suggested_fix="StoryEngine.create_dummy_story를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        outline = load_json(project_path / "story" / "story_outline.json")

        title = topic["title"]
        plan = {
            "project_id": project["project_id"],
            "topic": title,
            "direction_mode": "dummy",
            "visual_style": "cinematic documentary (placeholder)",
            "tone": "curious and contemplative (placeholder)",
            "pacing": "slow_build (placeholder)",
            "scene_direction_rules": [
                "hook 장면은 강한 시각적 질문으로 시작한다 (placeholder)",
                "설명 장면은 한 장면에 하나의 개념만 다룬다 (placeholder)",
                "ending은 여운을 남기고 채널 정체성을 강화한다 (placeholder)",
            ],
            "narration_direction": {
                "voice_mood": "calm narrator (placeholder)",
                "speed": "medium",
                "sections": list(outline["structure"].keys()),
            },
            "visual_prompt_rules": [
                "채널 브랜드 스타일을 유지한다 (placeholder)",
                "텍스트 없는 이미지 프롬프트를 사용한다 (placeholder)",
            ],
            "risk_notes": [
                "더미 연출 계획 — 실제 연출 판단이 반영되지 않았다.",
            ],
            "created_at": _now_iso(),
            "disclaimer": DUMMY_DISCLAIMER,
        }
        folder = project_path / DIRECTION_DIR
        write_json(folder / PLAN_FILE, plan)
        write_json(
            folder / "creative_brief.json",
            {
                "project_id": project["project_id"],
                "direction_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "concept": f"'{title}'를 다큐멘터리 톤으로 풀어내는 컨셉 (placeholder)",
                "audience_promise": "끝까지 보면 새로운 관점을 얻는다 (placeholder)",
                "references": [],
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "direction_review.json",
            {
                "project_id": project["project_id"],
                "direction_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 연출 — 실제 검토는 Quality 단계 구현 후 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 연출 계획 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return plan

    def load_direction_plan(self, project_path: str | Path) -> dict:
        path = self.plan_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"direction_plan.json이 없습니다: {path}",
                location="DirectionEngine.load_direction_plan",
                suggested_fix="create_dummy_direction을 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_direction(self, project_path: str | Path) -> bool:
        plan = self.load_direction_plan(project_path)
        ADOSValidator.require_fields(
            plan, PLAN_REQUIRED_FIELDS, location="DirectionEngine.validate_direction"
        )
        return True
