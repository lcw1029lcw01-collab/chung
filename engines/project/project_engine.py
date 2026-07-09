# -*- coding: utf-8 -*-
"""Project engine (walking skeleton).

projects/{channel_id}/{year}/{month}/{project_id}/ 아래에
project.json, topic.json과 표준 하위 폴더를 만든다.

- Project ID 규칙: docs/07_PROJECT_SPEC.md #7 (YYYYMMDD-HHMMSS-{channel_id}-{topic_slug})
- project.json / topic.json 최소 형태: docs/07_PROJECT_SPEC.md #9~10
"""
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSPathManager,
    ADOSValidator,
    ProjectStatus,
    StageName,
    ensure_directory,
    load_yaml,
    write_json,
)

PROJECT_REQUEST_FIELDS = ["channel_id", "topic", "target_languages", "duration_seconds"]

PROJECT_SUBFOLDERS = [
    "research",
    "knowledge",
    "story",
    "direction",
    "timeline",
    "prompts",
    "assets",
    "assets/images",
    "assets/motion",
    "assets/audio",
    "assets/subtitles",
    "edit",
    "reports",
    "workflow",
    "workflow/handoffs",
    "workflow/stage_results",
    "logs",
    "package",
    "analytics",
    "learning",
    "ai_evolution",
]

_MAX_SLUG_WORDS = 8


def make_topic_slug(topic: str) -> str:
    """소문자, 공백/특수문자 금지, 5~8단어 축약 (docs/07 #7)."""
    ascii_only = re.sub(r"[^a-zA-Z0-9\s-]", " ", topic)
    words = [w for w in re.split(r"[\s-]+", ascii_only.lower()) if w]
    if not words:
        return "topic"
    return "-".join(words[:_MAX_SLUG_WORDS])


class ProjectEngine:
    def __init__(self, path_manager: ADOSPathManager | None = None, logger: ADOSLogger | None = None):
        self.paths = path_manager or ADOSPathManager()
        self.logger = logger

    def _resolve_timezone(self):
        """config/ados.yaml의 timezone을 사용한다.

        config가 없거나(테스트 임시 루트 등) 시스템에 tz 데이터가 없어
        ZoneInfo 로드가 실패하면 UTC로 동작한다.
        """
        try:
            config = load_yaml(self.paths.config / "ados.yaml")
            tz_name = config.get("timezone") if isinstance(config, dict) else None
            if tz_name:
                return ZoneInfo(tz_name)
        except Exception:
            pass
        return timezone.utc

    def create_project(self, request: dict) -> dict:
        ADOSValidator.require_fields(
            request, PROJECT_REQUEST_FIELDS, location="ProjectEngine.create_project"
        )
        channel_id = request["channel_id"]

        channel_yaml = self.paths.channels / channel_id / "channel.yaml"
        if not channel_yaml.is_file():
            raise ADOSFileNotFoundError(
                f"채널이 존재하지 않습니다: {channel_id}",
                location="ProjectEngine.create_project",
                suggested_fix="ChannelEngine.create_channel로 채널을 먼저 생성하세요.",
            )
        channel = load_yaml(channel_yaml)

        now = datetime.now(self._resolve_timezone())
        # topic_slug가 오면 그것을 정제해 사용, 없으면 topic에서 생성 (기존 동작)
        slug = make_topic_slug(request.get("topic_slug") or request["topic"])
        project_id = f"{now:%Y%m%d}-{now:%H%M%S}-{channel_id}-{slug}"

        base = self.paths.projects / channel_id / f"{now:%Y}" / f"{now:%m}"
        folder = base / project_id
        suffix = 2
        while folder.exists():  # 동일 시간 생성 충돌 시 suffix (docs/07 #7)
            folder = base / f"{project_id}-{suffix:02d}"
            suffix += 1
        project_id = folder.name

        for sub in PROJECT_SUBFOLDERS:
            ensure_directory(folder / sub)

        created_at = now.isoformat()
        project_data = {
            "project_id": project_id,
            "project_name": request["topic"],
            "version": "1.0.0",
            "status": str(ProjectStatus.INITIALIZED),
            "current_stage": str(StageName.RESEARCH),
            "created_at": created_at,
            "updated_at": created_at,
            "company": {"name": "CHUNG COMPANY", "system": "ADOS"},
            "channel": {
                "channel_id": channel_id,
                "channel_name": channel.get("channel_name", ""),
                "template_id": channel.get("template_id", ""),
                "template_version": channel.get("template_version", ""),
            },
            "topic": {
                "topic_id": slug,
                "topic_source": "USER",
                "title": request["topic"],
            },
            "languages": {
                "master_language": channel.get("language", "ko"),
                "target_languages": list(request["target_languages"]),
            },
            "duration": {"target_seconds": int(request["duration_seconds"])},
        }
        write_json(folder / "project.json", project_data)

        topic_data = {
            "topic_id": slug,
            "source": "USER",
            "title": request["topic"],
            "slug": slug,
            "category": channel_id,
            "keywords": [],
            "target_audience": [],
            "topic_score": None,
            "growth_notes": [],
            "risk_notes": [],
        }
        write_json(folder / "topic.json", topic_data)

        if self.logger:
            self.logger.info(
                f"프로젝트 생성: {project_id}",
                metadata={"project_id": project_id, "channel_id": channel_id},
            )
        return {"project_id": project_id, "path": str(folder), "project": project_data}
