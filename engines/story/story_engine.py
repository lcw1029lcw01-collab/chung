# -*- coding: utf-8 -*-
"""Story engine (walking skeleton).

더미 지식을 기반으로 더미 스토리 산출물을 만든다.
전체 스키마는 docs/19_STORY_ENGINE.md 기준으로 이후 확장한다.

주의: 실제 대본 품질 로직은 없다. 모든 출력은 dummy이다.
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

STORY_DIR = "story"
OUTLINE_FILE = "story_outline.json"

OUTLINE_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "story_mode",
    "structure",
    "target_languages",
    "created_at",
]

STRUCTURE_REQUIRED_FIELDS = ["hook", "setup", "development", "payoff", "ending"]

DUMMY_DISCLAIMER = "Dummy script draft. Not production-ready."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class StoryEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def outline_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / STORY_DIR / OUTLINE_FILE

    def create_dummy_story(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        map_path = project_path / "knowledge" / "knowledge_map.json"
        if not map_path.is_file():
            raise ADOSFileNotFoundError(
                f"knowledge_map.json이 없습니다: {map_path}",
                location="StoryEngine.create_dummy_story",
                suggested_fix="KnowledgeEngine.create_dummy_knowledge를 먼저 실행하세요.",
            )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        knowledge_map = load_json(map_path)

        title = topic["title"]
        structure = {
            "hook": f"'{title}' — 시청자의 호기심을 여는 질문 (placeholder)",
            "setup": f"핵심 개념 소개: {knowledge_map['core_concept']}",
            "development": "지지 포인트들을 순서대로 전개 (placeholder)",
            "payoff": "핵심 질문에 대한 답 제시 (placeholder)",
            "ending": "여운을 남기는 마무리와 다음 영상 예고 (placeholder)",
        }
        outline = {
            "project_id": project["project_id"],
            "topic": title,
            "story_mode": "dummy",
            "disclaimer": DUMMY_DISCLAIMER,
            "structure": structure,
            "target_languages": project["languages"]["target_languages"],
            "created_at": _now_iso(),
        }

        duration = int(project["duration"]["target_seconds"])
        narration_blocks = [
            {"block_id": f"NB{i:03d}", "section": section, "text": text}
            for i, (section, text) in enumerate(structure.items(), start=1)
        ]
        script_draft = {
            "project_id": project["project_id"],
            "language": "ko",
            "script_mode": "dummy",
            "title": title,
            "narration_blocks": narration_blocks,
            "estimated_duration_seconds": duration,
            "disclaimer": DUMMY_DISCLAIMER,
            "created_at": _now_iso(),
        }

        folder = project_path / STORY_DIR
        write_json(folder / OUTLINE_FILE, outline)
        write_json(folder / "script_draft.json", script_draft)
        write_json(
            folder / "story_review.json",
            {
                "project_id": project["project_id"],
                "story_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 스토리 — 실제 품질 검토는 Quality 단계 구현 후 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 스토리 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return outline

    def load_story_outline(self, project_path: str | Path) -> dict:
        path = self.outline_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"story_outline.json이 없습니다: {path}",
                location="StoryEngine.load_story_outline",
                suggested_fix="create_dummy_story를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_story(self, project_path: str | Path) -> bool:
        outline = self.load_story_outline(project_path)
        ADOSValidator.require_fields(
            outline, OUTLINE_REQUIRED_FIELDS, location="StoryEngine.validate_story"
        )
        ADOSValidator.require_fields(
            outline["structure"], STRUCTURE_REQUIRED_FIELDS,
            location="StoryEngine.validate_story:structure",
        )
        return True
