# -*- coding: utf-8 -*-
"""Channel engine (walking skeleton).

channels/{channel_id}/ 아래에 channel.yaml, memory.yaml, reports/, logs/를 만든다.
전체 Channel System(템플릿 파일 복사, 스냅샷 등)은 docs/09 기준으로 이후에 구현한다.
"""
from datetime import datetime, timezone

from core import (
    ADOSLogger,
    ADOSPathManager,
    ADOSValidationError,
    ADOSValidator,
    ensure_directory,
    write_yaml,
)
from engines.template import TemplateLoader

CHANNEL_REQUEST_FIELDS = ["channel_id", "channel_name", "template_id", "language"]


class ChannelEngine:
    def __init__(self, path_manager: ADOSPathManager | None = None, logger: ADOSLogger | None = None):
        self.paths = path_manager or ADOSPathManager()
        self.logger = logger
        self.template_loader = TemplateLoader(self.paths)

    def channel_dir(self, channel_id: str):
        return self.paths.channels / channel_id

    def create_channel(self, request: dict) -> dict:
        ADOSValidator.require_fields(
            request, CHANNEL_REQUEST_FIELDS, location="ChannelEngine.create_channel"
        )
        channel_id = request["channel_id"]

        # Template이 없으면 구조화된 에러 (TemplateLoader가 던진다)
        template = self.template_loader.load(request["template_id"])

        folder = self.channel_dir(channel_id)
        if (folder / "channel.yaml").is_file():
            raise ADOSValidationError(
                f"이미 존재하는 채널입니다: {channel_id}",
                location="ChannelEngine.create_channel",
                suggested_fix="다른 channel_id를 사용하거나 기존 채널을 사용하세요.",
            )

        ensure_directory(folder)
        ensure_directory(folder / "reports")
        ensure_directory(folder / "logs")

        now = datetime.now(timezone.utc).isoformat()
        channel_data = {
            "channel_id": channel_id,
            "channel_name": request["channel_name"],
            "template_id": request["template_id"],
            "template_version": str(template["version"]),
            "language": request["language"],
            "status": "ACTIVE",
            "created_at": now,
        }
        write_yaml(folder / "channel.yaml", channel_data)

        memory_data = {
            "channel_id": channel_id,
            "created_at": now,
            "success_patterns": [],
            "failure_patterns": [],
            "notes": [],
        }
        write_yaml(folder / "memory.yaml", memory_data)

        if self.logger:
            self.logger.info(
                f"채널 생성: {channel_id}",
                metadata={"channel_id": channel_id, "template_id": request["template_id"]},
            )
        return {"channel_id": channel_id, "path": str(folder), "channel": channel_data}
