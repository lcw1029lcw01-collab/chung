# -*- coding: utf-8 -*-
"""Quality engine (walking skeleton).

모든 상위 계획을 확인하고 더미 품질 보고서를 만든다.
전체 스키마는 docs/26_QUALITY_ENGINE.md 기준으로 이후 확장한다.

주의: 실제 품질 검증이 아니다. skeleton이 다음 단계로 진행할 수 있도록
점수를 95로 줄 뿐이며 production_ready는 false를 유지한다.
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

REPORTS_DIR = "reports"
REPORT_FILE = "quality_report.json"
GATE_FILE = "quality_gate.json"

REQUIRED_INPUTS = [
    ("edit/editing_plan.json", "EditingEngine.create_dummy_editing_plan"),
    ("timeline/timeline.json", "TimelineEngine.create_dummy_timeline"),
    ("assets/images/visual_plan.json", "VisualEngine.create_dummy_visual_plan"),
    ("assets/motion/motion_plan.json", "MotionEngine.create_dummy_motion_plan"),
    ("assets/audio/voice_plan.json", "VoiceEngine.create_dummy_voice_plan"),
    ("assets/subtitles/subtitle_plan.json", "SubtitleEngine.create_dummy_subtitle_plan"),
]

REPORT_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "quality_mode",
    "total_score",
    "decision",
    "production_ready",
    "checked_items",
    "risks",
    "recommendations",
    "created_at",
    "disclaimer",
]

DUMMY_DISCLAIMER = "Dummy quality report. Not a real production quality assessment."

# 더미 점수 — skeleton이 PASS 게이트를 통과해 다음 단계로 진행하기 위한 값
_DUMMY_SCORE = 95


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class QualityEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / REPORT_FILE

    def gate_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / GATE_FILE

    def create_dummy_quality_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for rel, fix in REQUIRED_INPUTS:
            if not (project_path / rel).is_file():
                raise ADOSFileNotFoundError(
                    f"{rel}가 없습니다: {project_path / rel}",
                    location="QualityEngine.create_dummy_quality_report",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        load_json(project_path / "edit" / "editing_plan.json")  # 파싱 검증

        report = {
            "project_id": project["project_id"],
            "topic": topic["title"],
            "quality_mode": "dummy",
            "total_score": _DUMMY_SCORE,
            "decision": "PASS",
            "production_ready": False,
            "checked_items": [
                {"item": rel, "status": "EXISTS", "note": "존재 확인만 수행 (dummy)"}
                for rel, _ in REQUIRED_INPUTS
            ],
            "risks": [
                "실제 품질 검증이 수행되지 않았다 — 모든 상위 산출물이 dummy이다.",
            ],
            "recommendations": [
                "실제 Quality Engine 구현 후 이 보고서를 재생성해야 한다.",
            ],
            "created_at": _now_iso(),
            "disclaimer": DUMMY_DISCLAIMER,
        }
        folder = project_path / REPORTS_DIR
        write_json(folder / REPORT_FILE, report)
        write_json(
            folder / GATE_FILE,
            {
                "project_id": project["project_id"],
                "total_score": _DUMMY_SCORE,
                "threshold_pass": 95,
                "threshold_human_check": 90,
                "threshold_auto_fix": 80,
                "gate_result": "PASS",
                "next_action": "PACKAGE",
                "auto_fix_required": False,
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "quality_review.json",
            {
                "project_id": project["project_id"],
                "quality_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 품질 보고 — 실제 검토는 Quality 엔진 구현 후 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 품질 보고서 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"], "score": _DUMMY_SCORE},
            )
        return report

    def load_quality_report(self, project_path: str | Path) -> dict:
        path = self.report_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"quality_report.json이 없습니다: {path}",
                location="QualityEngine.load_quality_report",
                suggested_fix="create_dummy_quality_report를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_quality_report(self, project_path: str | Path) -> bool:
        report = self.load_quality_report(project_path)
        ADOSValidator.require_fields(
            report, REPORT_REQUIRED_FIELDS,
            location="QualityEngine.validate_quality_report",
        )
        return True
