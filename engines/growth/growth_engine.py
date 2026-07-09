# -*- coding: utf-8 -*-
"""Growth engine (walking skeleton).

성과 스냅샷과 게시 계획을 기반으로 더미 성장 보고서를 만든다.
전체 스키마는 docs/27_GROWTH_ENGINE.md 기준으로 이후 확장한다.

주의: Growth는 현재 core.types.STAGE_ORDER의 워크플로우 단계가 아니다.
Analytics 이후의 자문(advisory) 출력으로만 취급한다.
실제 성장 최적화 결과를 지어내지 않는다.
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
REPORT_FILE = "growth_report.json"

REQUIRED_INPUTS = [
    ("analytics/performance_snapshot.json", "AnalyticsEngine.create_dummy_analytics"),
    ("package/publishing_plan.json", "PublishingEngine.create_dummy_package"),
]

REPORT_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "growth_mode",
    "data_ready",
    "causal_path",
    "hypotheses",
    "title_packaging_notes",
    "recommendation_notes",
    "next_experiments",
    "created_at",
    "disclaimer",
]

DUMMY_DISCLAIMER = "Dummy growth report. No real performance optimization has occurred."

CAUSAL_PATH = [
    "quality",
    "retention",
    "recommendation",
    "views",
    "subscribers",
    "revenue",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class GrowthEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / ANALYTICS_DIR / REPORT_FILE

    def create_dummy_growth_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for rel, fix in REQUIRED_INPUTS:
            if not (project_path / rel).is_file():
                raise ADOSFileNotFoundError(
                    f"{rel}가 없습니다: {project_path / rel}",
                    location="GrowthEngine.create_dummy_growth_report",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        snapshot = load_json(project_path / ANALYTICS_DIR / "performance_snapshot.json")
        publishing_plan = load_json(project_path / "package" / "publishing_plan.json")

        report = {
            "project_id": project["project_id"],
            "topic": topic["title"],
            "growth_mode": "dummy",
            "data_ready": bool(snapshot["data_ready"]),
            "causal_path": CAUSAL_PATH,
            "hypotheses": [
                {
                    "hypothesis_id": "GH001",
                    "statement": "훅 강도가 높을수록 초반 이탈이 줄어든다 (placeholder)",
                    "testable": False,
                    "reason_not_testable": "실제 성과 데이터가 없다.",
                }
            ],
            "title_packaging_notes": [
                f"현재 제목(placeholder): {publishing_plan['title']}",
                "실제 CTR 데이터 확보 후 제목/썸네일 A/B 테스트 필요.",
            ],
            "recommendation_notes": [
                "추천 노출 최적화는 실제 시청 데이터가 쌓인 뒤에만 의미가 있다.",
            ],
            "next_experiments": [
                "훅 스타일 2종 비교 (placeholder)",
            ],
            "created_at": _now_iso(),
            "disclaimer": DUMMY_DISCLAIMER,
        }
        folder = project_path / ANALYTICS_DIR
        write_json(folder / REPORT_FILE, report)
        write_json(
            folder / "growth_hypotheses.json",
            {
                "project_id": project["project_id"],
                "growth_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "hypotheses": report["hypotheses"],
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "growth_review.json",
            {
                "project_id": project["project_id"],
                "growth_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 성장 보고 — 실제 데이터 확보 전까지 자문 출력일 뿐이다."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 성장 보고서 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return report

    def load_growth_report(self, project_path: str | Path) -> dict:
        path = self.report_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"growth_report.json이 없습니다: {path}",
                location="GrowthEngine.load_growth_report",
                suggested_fix="create_dummy_growth_report를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_growth_report(self, project_path: str | Path) -> bool:
        report = self.load_growth_report(project_path)
        ADOSValidator.require_fields(
            report, REPORT_REQUIRED_FIELDS,
            location="GrowthEngine.validate_growth_report",
        )
        return True
