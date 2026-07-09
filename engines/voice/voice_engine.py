# -*- coding: utf-8 -*-
"""Voice engine (walking skeleton).

대본 초안과 타임라인을 기반으로 더미 음성 계획을 만든다.
전체 스키마는 docs/23_VOICE_ENGINE.md 기준으로 이후 확장한다.

주의: Typecast를 호출하지 않는다. 오디오 파일을 만들지 않는다.
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

AUDIO_DIR = Path("assets") / "audio"
PLAN_FILE = "voice_plan.json"

PLAN_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "voice_mode",
    "provider_hint",
    "language",
    "production_ready",
    "disclaimer",
    "narration_blocks",
    "estimated_duration_seconds",
    "created_at",
]

NARRATION_BLOCK_REQUIRED_FIELDS = [
    "block_id",
    "text",
    "estimated_duration_seconds",
    "voice_style",
    "status",
]

DUMMY_DISCLAIMER = "Dummy voice plan. No real audio generated."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class VoiceEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def plan_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / AUDIO_DIR / PLAN_FILE

    def create_dummy_voice_plan(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for required, fix in (
            ("story/script_draft.json", "StoryEngine.create_dummy_story"),
            ("timeline/timeline.json", "TimelineEngine.create_dummy_timeline"),
        ):
            if not (project_path / required).is_file():
                raise ADOSFileNotFoundError(
                    f"{required}가 없습니다: {project_path / required}",
                    location="VoiceEngine.create_dummy_voice_plan",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        script = load_json(project_path / "story" / "script_draft.json")
        load_json(project_path / "timeline" / "timeline.json")  # 존재 검증

        total = int(script["estimated_duration_seconds"])
        blocks = script["narration_blocks"]
        per_block = max(1, total // max(1, len(blocks)))
        narration_blocks = [
            {
                "block_id": block["block_id"],
                "text": block["text"],
                "estimated_duration_seconds": per_block,
                "voice_style": "calm narrator (placeholder)",
                "status": "PLANNED",
            }
            for block in blocks
        ]

        plan = {
            "project_id": project["project_id"],
            "topic": topic["title"],
            "voice_mode": "dummy",
            "provider_hint": "typecast",
            "language": "ko",
            "production_ready": False,
            "disclaimer": DUMMY_DISCLAIMER,
            "narration_blocks": narration_blocks,
            "estimated_duration_seconds": total,
            "created_at": _now_iso(),
        }
        folder = project_path / AUDIO_DIR
        write_json(folder / PLAN_FILE, plan)
        write_json(
            folder / "voice_manifest.json",
            {
                "project_id": project["project_id"],
                "voice_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "audio_files": [],  # 실제 오디오는 생성하지 않는다
                "expected_audio": [
                    {"block_id": nb["block_id"], "status": "PLANNED"}
                    for nb in narration_blocks
                ],
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "voice_review.json",
            {
                "project_id": project["project_id"],
                "voice_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 음성 계획 — 실제 음성 검토는 이후 단계에서 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 음성 계획 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"], "blocks": len(narration_blocks)},
            )
        return plan

    def load_voice_plan(self, project_path: str | Path) -> dict:
        path = self.plan_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"voice_plan.json이 없습니다: {path}",
                location="VoiceEngine.load_voice_plan",
                suggested_fix="create_dummy_voice_plan을 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_voice_plan(self, project_path: str | Path) -> bool:
        plan = self.load_voice_plan(project_path)
        loc = "VoiceEngine.validate_voice_plan"
        ADOSValidator.require_fields(plan, PLAN_REQUIRED_FIELDS, location=loc)
        for nb in plan["narration_blocks"]:
            ADOSValidator.require_fields(nb, NARRATION_BLOCK_REQUIRED_FIELDS, location=loc)
        return True
