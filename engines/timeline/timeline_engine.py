# -*- coding: utf-8 -*-
"""Timeline engine (walking skeleton).

project.json/topic.json을 읽어 3-장면 더미 타임라인을 만든다.
전체 Timeline 스키마는 docs/16_TIMELINE_ENGINE.md 기준으로 이후 확장한다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    load_json,
    write_json,
)

from .timeline_validator import TimelineValidator

TIMELINE_DIR = "timeline"
TIMELINE_FILE = "timeline.json"
REVIEW_FILE = "timeline_review.json"
LOCK_FILE = "timeline_lock.json"

# 더미 3장면의 길이 배분 비율 (hook / explanation / ending)
_HOOK_RATIO = 0.15
_ENDING_RATIO = 0.15


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TimelineEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def timeline_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / TIMELINE_DIR / TIMELINE_FILE

    def create_dummy_timeline(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        load_json(project_path / "topic.json")  # 존재 검증 (없으면 구조화 에러)

        duration = int(project["duration"]["target_seconds"])
        hook = max(1, round(duration * _HOOK_RATIO))
        ending = max(1, round(duration * _ENDING_RATIO))
        explanation = duration - hook - ending

        def scene(scene_id, order, purpose, seconds, motion_required, motion_reason):
            return {
                "scene_id": scene_id,
                "order": order,
                "purpose": purpose,
                "duration_seconds": seconds,
                "visual": {"required": True},
                "voice": {"required": True},
                "subtitle": {"required": True},
                "motion": {"required": motion_required, "reason": motion_reason},
            }

        timeline = {
            "project_id": project["project_id"],
            "channel_id": project["channel"]["channel_id"],
            "total_duration_seconds": duration,
            "target_languages": project["languages"]["target_languages"],
            "status": "DRAFT",
            "created_at": _now_iso(),
            "scenes": [
                scene("SC001", 1, "hook", hook, True, "hook_scene"),
                scene("SC002", 2, "explanation", explanation, False, None),
                scene("SC003", 3, "ending", ending, False, None),
            ],
        }
        TimelineValidator.validate(timeline)

        folder = project_path / TIMELINE_DIR
        write_json(folder / TIMELINE_FILE, timeline)
        write_json(
            folder / REVIEW_FILE,
            {
                "project_id": timeline["project_id"],
                "status": "PENDING_REVIEW",
                "validated": True,
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / LOCK_FILE,
            {"project_id": timeline["project_id"], "locked": False, "locked_at": None},
        )
        if self.logger:
            self.logger.info(
                f"더미 타임라인 생성: {timeline['project_id']}",
                metadata={"project_id": timeline["project_id"], "scenes": 3},
            )
        return timeline

    def load_timeline(self, project_path: str | Path) -> dict:
        path = self.timeline_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"timeline.json이 없습니다: {path}",
                location="TimelineEngine.load_timeline",
                suggested_fix="create_dummy_timeline을 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_timeline(self, project_path: str | Path) -> bool:
        TimelineValidator.validate(self.load_timeline(project_path))
        return True

    def lock_timeline(self, project_path: str | Path) -> dict:
        self.validate_timeline(project_path)  # 검증 통과 후에만 잠근다
        lock = {
            "project_id": self.load_timeline(project_path)["project_id"],
            "locked": True,
            "locked_at": _now_iso(),
        }
        write_json(Path(project_path) / TIMELINE_DIR / LOCK_FILE, lock)
        return lock
