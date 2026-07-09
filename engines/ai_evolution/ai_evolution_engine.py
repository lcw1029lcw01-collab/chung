# -*- coding: utf-8 -*-
"""AI Evolution engine (walking skeleton).

학습 산출물을 기반으로 더미 진화 보고서를 만든다.
전체 스키마는 docs/31_AI_EVOLUTION_ENGINE.md 기준으로 이후 확장한다.

주의: 학습 결과로 코드를 수정하지 않는다. Memory를 갱신하지 않는다.
시스템 자기개선은 수행하지 않는다. placeholder JSON만 작성한다.
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

AI_EVOLUTION_DIR = "ai_evolution"
REPORT_FILE = "ai_evolution_report.json"

REQUIRED_INPUTS = [
    ("learning/learning_report.json", "LearningEngine.create_dummy_learning_report"),
    ("learning/improvement_backlog.json", "LearningEngine.create_dummy_learning_report"),
]

REPORT_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "ai_evolution_mode",
    "data_ready",
    "proposed_system_changes",
    "rejected_changes",
    "risk_notes",
    "memory_update_required",
    "code_change_required",
    "created_at",
    "disclaimer",
]

DUMMY_DISCLAIMER = (
    "Dummy AI evolution report. No autonomous system changes were applied."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AIEvolutionEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / AI_EVOLUTION_DIR / REPORT_FILE

    def create_dummy_ai_evolution_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for rel, fix in REQUIRED_INPUTS:
            if not (project_path / rel).is_file():
                raise ADOSFileNotFoundError(
                    f"{rel}가 없습니다: {project_path / rel}",
                    location="AIEvolutionEngine.create_dummy_ai_evolution_report",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        learning = load_json(project_path / "learning" / "learning_report.json")

        report = {
            "project_id": project["project_id"],
            "topic": topic["title"],
            "ai_evolution_mode": "dummy",
            "data_ready": bool(learning["data_ready"]),
            "proposed_system_changes": [
                {
                    "change_id": "EV001",
                    "title": "dummy 엔진을 실제 엔진으로 교체 (placeholder)",
                    "risk_level": "LOW",
                    "status": "PROPOSED_ONLY",
                }
            ],
            "rejected_changes": [],
            "risk_notes": [
                "실제 성과 데이터가 없어 어떤 시스템 변경도 적용하지 않았다.",
            ],
            "memory_update_required": False,
            "code_change_required": False,
            "created_at": _now_iso(),
            "disclaimer": DUMMY_DISCLAIMER,
        }
        folder = project_path / AI_EVOLUTION_DIR
        write_json(folder / REPORT_FILE, report)
        write_json(
            folder / "system_reflection.json",
            {
                "project_id": project["project_id"],
                "ai_evolution_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "pipeline_observations": [
                    "walking skeleton 전 단계가 순서대로 완주했다 (구조 검증).",
                ],
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "evolution_backlog.json",
            {
                "project_id": project["project_id"],
                "backlog_mode": "dummy",
                "items": [
                    {
                        "item_id": "EB001",
                        "title": "실제 데이터 기반 진화 제안으로 교체",
                        "status": "PLANNED",
                    }
                ],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 AI 진화 보고서 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return report

    def load_ai_evolution_report(self, project_path: str | Path) -> dict:
        path = self.report_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"ai_evolution_report.json이 없습니다: {path}",
                location="AIEvolutionEngine.load_ai_evolution_report",
                suggested_fix="create_dummy_ai_evolution_report를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_ai_evolution_report(self, project_path: str | Path) -> bool:
        report = self.load_ai_evolution_report(project_path)
        ADOSValidator.require_fields(
            report, REPORT_REQUIRED_FIELDS,
            location="AIEvolutionEngine.validate_ai_evolution_report",
        )
        return True
