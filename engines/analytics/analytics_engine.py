# -*- coding: utf-8 -*-
"""Analytics engine (walking skeleton).

게시 기록을 기반으로 더미 성과 스냅샷을 만든다.
전체 스키마는 docs/29_ANALYTICS_ENGINE.md 기준으로 이후 확장한다.

주의: YouTube Analytics를 호출하지 않는다. 실제 성과를 지어내지 않는다.
모든 지표는 0/placeholder이며 data_ready는 false다.
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

ANALYTICS_DIR = "analytics"
SNAPSHOT_FILE = "performance_snapshot.json"

SNAPSHOT_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "analytics_mode",
    "publication_status",
    "views",
    "impressions",
    "click_through_rate",
    "average_view_duration_seconds",
    "retention_rate",
    "subscribers_gained",
    "revenue_estimate",
    "data_ready",
    "created_at",
    "disclaimer",
]

DUMMY_DISCLAIMER = "Dummy analytics snapshot. No real platform data collected."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AnalyticsEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def snapshot_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / ANALYTICS_DIR / SNAPSHOT_FILE

    def create_dummy_analytics(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        record_path = project_path / "package" / "published_record.json"
        if not record_path.is_file():
            raise ADOSFileNotFoundError(
                f"published_record.json이 없습니다: {record_path}",
                location="AnalyticsEngine.create_dummy_analytics",
                suggested_fix="PublishingEngine.create_dummy_published_record를 먼저 실행하세요.",
            )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        record = load_json(record_path)

        snapshot = {
            "project_id": project["project_id"],
            "topic": topic["title"],
            "analytics_mode": "dummy",
            "publication_status": record["publication_status"],
            "views": 0,
            "impressions": 0,
            "click_through_rate": 0.0,
            "average_view_duration_seconds": 0,
            "retention_rate": 0.0,
            "subscribers_gained": 0,
            "revenue_estimate": 0.0,
            "data_ready": False,
            "created_at": _now_iso(),
            "disclaimer": DUMMY_DISCLAIMER,
        }
        folder = project_path / ANALYTICS_DIR
        write_json(
            folder / "analytics_plan.json",
            {
                "project_id": project["project_id"],
                "analytics_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "metrics_to_track": [
                    "views", "impressions", "click_through_rate",
                    "average_view_duration_seconds", "retention_rate",
                    "subscribers_gained", "revenue_estimate",
                ],
                "collection_blocked_reason": "실제 업로드가 없어 수집할 데이터가 없다.",
                "created_at": _now_iso(),
            },
        )
        write_json(folder / SNAPSHOT_FILE, snapshot)
        write_json(
            folder / "analytics_review.json",
            {
                "project_id": project["project_id"],
                "analytics_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 성과 스냅샷 — 실제 데이터 수집은 게시 이후 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 성과 스냅샷 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return snapshot

    def load_analytics_snapshot(self, project_path: str | Path) -> dict:
        path = self.snapshot_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"performance_snapshot.json이 없습니다: {path}",
                location="AnalyticsEngine.load_analytics_snapshot",
                suggested_fix="create_dummy_analytics를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_analytics(self, project_path: str | Path) -> bool:
        snapshot = self.load_analytics_snapshot(project_path)
        ADOSValidator.require_fields(
            snapshot, SNAPSHOT_REQUIRED_FIELDS,
            location="AnalyticsEngine.validate_analytics",
        )
        return True
