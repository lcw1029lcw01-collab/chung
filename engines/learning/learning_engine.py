# -*- coding: utf-8 -*-
"""Learning engine (walking skeleton).

성과 스냅샷을 기반으로 더미 학습 보고서를 만든다.
전체 스키마는 docs/30_LEARNING_ENGINE.md 기준으로 이후 확장한다.

주의: 장기 Memory를 갱신하지 않는다. AI Evolution을 구현하지 않는다.
실제 성과 학습은 일어나지 않는다.
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

LEARNING_DIR = "learning"
REPORT_FILE = "learning_report.json"

REPORT_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "learning_mode",
    "data_ready",
    "lessons",
    "improvement_ideas",
    "next_experiment_candidates",
    "memory_update_required",
    "created_at",
    "disclaimer",
]

DUMMY_DISCLAIMER = "Dummy learning report. No real performance learning has occurred."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LearningEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / LEARNING_DIR / REPORT_FILE

    def create_dummy_learning_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        snapshot_path = project_path / "analytics" / "performance_snapshot.json"
        if not snapshot_path.is_file():
            raise ADOSFileNotFoundError(
                f"performance_snapshot.json이 없습니다: {snapshot_path}",
                location="LearningEngine.create_dummy_learning_report",
                suggested_fix="AnalyticsEngine.create_dummy_analytics를 먼저 실행하세요.",
            )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        snapshot = load_json(snapshot_path)

        report = {
            "project_id": project["project_id"],
            "topic": topic["title"],
            "learning_mode": "dummy",
            "data_ready": bool(snapshot["data_ready"]),
            "lessons": [
                "파이프라인 walking skeleton이 끝까지 연결되는 것을 확인했다 (구조 검증).",
            ],
            "improvement_ideas": [
                "각 dummy 엔진을 실제 엔진으로 교체 (placeholder)",
            ],
            "next_experiment_candidates": [
                "실제 데이터 확보 후 훅 스타일 A/B 테스트 (placeholder)",
            ],
            "memory_update_required": False,
            "created_at": _now_iso(),
            "disclaimer": DUMMY_DISCLAIMER,
        }
        folder = project_path / LEARNING_DIR
        write_json(folder / REPORT_FILE, report)
        write_json(
            folder / "improvement_backlog.json",
            {
                "project_id": project["project_id"],
                "backlog_mode": "dummy",
                "items": [
                    {
                        "item_id": "BL001",
                        "title": "실제 성과 데이터 기반 학습으로 교체",
                        "priority": "HIGH",
                        "status": "PLANNED",
                    }
                ],
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "learning_review.json",
            {
                "project_id": project["project_id"],
                "learning_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 학습 보고 — 장기 Memory 갱신 없음."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 학습 보고서 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return report

    def load_learning_report(self, project_path: str | Path) -> dict:
        path = self.report_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"learning_report.json이 없습니다: {path}",
                location="LearningEngine.load_learning_report",
                suggested_fix="create_dummy_learning_report를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_learning_report(self, project_path: str | Path) -> bool:
        report = self.load_learning_report(project_path)
        ADOSValidator.require_fields(
            report, REPORT_REQUIRED_FIELDS,
            location="LearningEngine.validate_learning_report",
        )
        return True
