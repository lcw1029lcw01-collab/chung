# -*- coding: utf-8 -*-
"""ADOS logger.

- 텍스트 로그: logs/ados.log
- JSONL 이벤트 로그: logs/events.jsonl
필드: timestamp, level, component, message, metadata
로그 대상 규칙: docs/02_DEVELOPMENT_RULES.md #11
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from .file_loader import ensure_directory
from .types import LogLevel

TEXT_LOG_FILENAME = "ados.log"
EVENT_LOG_FILENAME = "events.jsonl"


class ADOSLogger:
    def __init__(self, component: str, logs_dir: str | Path):
        self.component = component
        self.logs_dir = ensure_directory(logs_dir)
        self.text_log_path = self.logs_dir / TEXT_LOG_FILENAME
        self.event_log_path = self.logs_dir / EVENT_LOG_FILENAME

    def log(self, level: LogLevel | str, message: str, metadata: dict | None = None) -> dict:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": str(level),
            "component": self.component,
            "message": message,
            "metadata": metadata or {},
        }
        self._write_text(event)
        self._write_event(event)
        return event

    def debug(self, message: str, metadata: dict | None = None) -> dict:
        return self.log(LogLevel.DEBUG, message, metadata)

    def info(self, message: str, metadata: dict | None = None) -> dict:
        return self.log(LogLevel.INFO, message, metadata)

    def warning(self, message: str, metadata: dict | None = None) -> dict:
        return self.log(LogLevel.WARNING, message, metadata)

    def error(self, message: str, metadata: dict | None = None) -> dict:
        return self.log(LogLevel.ERROR, message, metadata)

    def _write_text(self, event: dict) -> None:
        line = f"{event['timestamp']} [{event['level']}] {event['component']}: {event['message']}\n"
        with open(self.text_log_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line)

    def _write_event(self, event: dict) -> None:
        with open(self.event_log_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
