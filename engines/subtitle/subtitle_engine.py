# -*- coding: utf-8 -*-
"""Subtitle engine (walking skeleton).

음성 계획과 대본을 기반으로 더미 자막 계획을 만든다.
전체 스키마는 docs/24_SUBTITLE_ENGINE.md 기준으로 이후 확장한다.

주의: .srt/.vtt 파일은 만들지 않는다. JSON 계획만 생성한다.
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

SUBTITLES_DIR = Path("assets") / "subtitles"
PLAN_FILE = "subtitle_plan.json"

PLAN_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "subtitle_mode",
    "source_language",
    "target_languages",
    "production_ready",
    "disclaimer",
    "subtitle_blocks",
    "created_at",
]

SUBTITLE_BLOCK_REQUIRED_FIELDS = [
    "block_id",
    "language",
    "text",
    "start_seconds",
    "end_seconds",
    "status",
]

DUMMY_DISCLAIMER = "Dummy subtitle plan. No real subtitle files generated."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SubtitleEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def plan_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / SUBTITLES_DIR / PLAN_FILE

    def create_dummy_subtitle_plan(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for required, fix in (
            ("assets/audio/voice_plan.json", "VoiceEngine.create_dummy_voice_plan"),
            ("story/script_draft.json", "StoryEngine.create_dummy_story"),
        ):
            if not (project_path / required).is_file():
                raise ADOSFileNotFoundError(
                    f"{required}가 없습니다: {project_path / required}",
                    location="SubtitleEngine.create_dummy_subtitle_plan",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        voice_plan = load_json(project_path / "assets" / "audio" / "voice_plan.json")
        load_json(project_path / "story" / "script_draft.json")  # 존재 검증

        target_languages = project["languages"]["target_languages"]
        source_language = voice_plan["language"]

        subtitle_blocks = []
        for language in target_languages:
            cursor = 0
            for nb in voice_plan["narration_blocks"]:
                seconds = int(nb["estimated_duration_seconds"])
                text = nb["text"]
                if language != source_language:
                    text = f"[{language} placeholder] {text}"
                subtitle_blocks.append(
                    {
                        "block_id": f"{nb['block_id']}-{language}",
                        "language": language,
                        "text": text,
                        "start_seconds": cursor,
                        "end_seconds": cursor + seconds,
                        "status": "PLANNED",
                    }
                )
                cursor += seconds

        plan = {
            "project_id": project["project_id"],
            "topic": topic["title"],
            "subtitle_mode": "dummy",
            "source_language": source_language,
            "target_languages": target_languages,
            "production_ready": False,
            "disclaimer": DUMMY_DISCLAIMER,
            "subtitle_blocks": subtitle_blocks,
            "created_at": _now_iso(),
        }
        folder = project_path / SUBTITLES_DIR
        write_json(folder / PLAN_FILE, plan)
        write_json(
            folder / "subtitle_manifest.json",
            {
                "project_id": project["project_id"],
                "subtitle_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "subtitle_files": [],  # .srt/.vtt는 아직 만들지 않는다
                "expected_files": [
                    {"language": lang, "format": "srt", "status": "PLANNED"}
                    for lang in target_languages
                ],
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "subtitle_review.json",
            {
                "project_id": project["project_id"],
                "subtitle_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 자막 계획 — 실제 자막 검토는 이후 단계에서 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 자막 계획 생성: {project['project_id']}",
                metadata={
                    "project_id": project["project_id"],
                    "blocks": len(subtitle_blocks),
                },
            )
        return plan

    def load_subtitle_plan(self, project_path: str | Path) -> dict:
        path = self.plan_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"subtitle_plan.json이 없습니다: {path}",
                location="SubtitleEngine.load_subtitle_plan",
                suggested_fix="create_dummy_subtitle_plan을 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_subtitle_plan(self, project_path: str | Path) -> bool:
        plan = self.load_subtitle_plan(project_path)
        loc = "SubtitleEngine.validate_subtitle_plan"
        ADOSValidator.require_fields(plan, PLAN_REQUIRED_FIELDS, location=loc)
        for sb in plan["subtitle_blocks"]:
            ADOSValidator.require_fields(sb, SUBTITLE_BLOCK_REQUIRED_FIELDS, location=loc)
        return True
