# -*- coding: utf-8 -*-
"""Run report generator (walking skeleton).

project.json과 workflow_state.json, 주요 산출물 존재 여부를 종합해
실행 보고서를 만든다.

주의: production 완료 보고서가 아니다. production_ready/upload_ready는
항상 false로 기록한다 (dummy 파이프라인이므로).
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
REPORT_FILE = "run_report.json"

# 전체 dummy 파이프라인이 만들어야 하는 산출물 목록
EXPECTED_OUTPUTS = [
    "research/research_brief.json",
    "research/research_questions.json",
    "research/source_plan.json",
    "knowledge/knowledge_map.json",
    "knowledge/fact_sheet.json",
    "knowledge/knowledge_gaps.json",
    "story/story_outline.json",
    "story/script_draft.json",
    "story/story_review.json",
    "direction/direction_plan.json",
    "direction/creative_brief.json",
    "direction/direction_review.json",
    "timeline/timeline.json",
    "timeline/timeline_review.json",
    "timeline/timeline_lock.json",
    "prompts/visual_prompts.json",
    "assets/images/image_manifest.json",
    "assets/images/visual_plan.json",
    "assets/images/visual_review.json",
    "assets/motion/motion_plan.json",
    "assets/motion/motion_manifest.json",
    "assets/motion/motion_review.json",
    "assets/audio/voice_plan.json",
    "assets/audio/voice_manifest.json",
    "assets/audio/voice_review.json",
    "assets/subtitles/subtitle_plan.json",
    "assets/subtitles/subtitle_manifest.json",
    "assets/subtitles/subtitle_review.json",
    "edit/editing_plan.json",
    "edit/assembly_manifest.json",
    "edit/editing_review.json",
    "reports/quality_report.json",
    "reports/quality_gate.json",
    "reports/quality_review.json",
    "package/package_manifest.json",
    "package/upload_package.json",
    "package/publishing_plan.json",
    "package/ready_state.json",
    "package/published_record.json",
    "analytics/analytics_plan.json",
    "analytics/performance_snapshot.json",
    "analytics/analytics_review.json",
    "analytics/growth_report.json",
    "analytics/growth_hypotheses.json",
    "analytics/growth_review.json",
    "learning/learning_report.json",
    "learning/improvement_backlog.json",
    "learning/learning_review.json",
    "ai_evolution/ai_evolution_report.json",
    "ai_evolution/system_reflection.json",
    "ai_evolution/evolution_backlog.json",
]

REPORT_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "run_mode",
    "final_stage",
    "completed_stages",
    "total_outputs_detected",
    "missing_expected_outputs",
    "production_ready",
    "upload_ready",
    "real_assets_present",
    "created_at",
    "disclaimer",
]

DUMMY_DISCLAIMER = "Dummy run report. This is not a production completion report."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunReportGenerator:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / REPORT_FILE

    def inventory_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / "output_inventory.json"

    def create_run_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        state_file = project_path / "workflow" / "workflow_state.json"
        if not state_file.is_file():
            raise ADOSFileNotFoundError(
                f"workflow_state.json이 없습니다: {state_file}",
                location="RunReportGenerator.create_run_report",
                suggested_fix="WorkflowOrchestrator.initialize_workflow를 먼저 실행하세요.",
            )
        state = load_json(state_file)

        inventory = [
            {"path": rel, "exists": (project_path / rel).is_file()}
            for rel in EXPECTED_OUTPUTS
        ]
        detected = [item["path"] for item in inventory if item["exists"]]
        missing = [item["path"] for item in inventory if not item["exists"]]

        report = {
            "project_id": project["project_id"],
            "topic": project["topic"]["title"],
            "run_mode": "dummy",
            "final_stage": state["current_stage"],
            "completed_stages": state["completed_stages"],
            "total_outputs_detected": len(detected),
            "missing_expected_outputs": missing,
            "production_ready": False,
            "upload_ready": False,
            "real_assets_present": False,
            "created_at": _now_iso(),
            "disclaimer": DUMMY_DISCLAIMER,
        }
        folder = project_path / REPORTS_DIR
        write_json(folder / REPORT_FILE, report)
        write_json(
            self.inventory_path(project_path),
            {
                "project_id": project["project_id"],
                "run_mode": "dummy",
                "expected_total": len(EXPECTED_OUTPUTS),
                "detected_total": len(detected),
                "outputs": inventory,
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "final_status_summary.json",
            {
                "project_id": project["project_id"],
                "run_mode": "dummy",
                "workflow_status": state["status"],
                "final_stage": state["current_stage"],
                "completed_stage_count": len(state["completed_stages"]),
                "outputs_detected": len(detected),
                "outputs_missing": len(missing),
                "production_ready": False,
                "upload_ready": False,
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"실행 보고서 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"], "detected": len(detected)},
            )
        return report

    def load_run_report(self, project_path: str | Path) -> dict:
        path = self.report_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"run_report.json이 없습니다: {path}",
                location="RunReportGenerator.load_run_report",
                suggested_fix="create_run_report를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_run_report(self, project_path: str | Path) -> bool:
        report = self.load_run_report(project_path)
        ADOSValidator.require_fields(
            report, REPORT_REQUIRED_FIELDS,
            location="RunReportGenerator.validate_run_report",
        )
        return True
