# -*- coding: utf-8 -*-
"""Operation report generator (upload-preparation skeleton).

전체 실행 상태를 종합해 사람에게 인수인계(handoff)하는 운영 보고서를 만든다.

주의: 실제 업로드/제작 자동화는 수행되지 않았다.
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
REPORT_FILE = "operation_report.json"

REQUIRED_INPUTS = [
    ("workflow/workflow_state.json", "WorkflowOrchestrator.initialize_workflow"),
    ("reports/final_quality_report.json", "FinalQualityGate.create_final_quality_report"),
    ("package/youtube_metadata_package.json", "UploadPreparer.create_youtube_metadata_package"),
    ("package/upload_readiness_checklist.json", "UploadPreparer.create_upload_readiness_checklist"),
    ("assets/asset_readiness_report.json", "AssetRegistry.create_asset_readiness_report"),
    ("reports/human_review_summary.json", "HumanReviewEngine.create_review_checkpoints"),
]

REPORT_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "operation_mode",
    "workflow_status",
    "completed_stages",
    "production_ready",
    "upload_ready",
    "real_assets_present",
    "human_review_approved",
    "final_quality_decision",
    "next_manual_actions",
    "created_at",
    "disclaimer",
]

DISCLAIMER = (
    "Operation report for manual handoff. "
    "No real upload or production automation was performed."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class OperationReportGenerator:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / REPORT_FILE

    def create_operation_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for rel, fix in REQUIRED_INPUTS:
            if not (project_path / rel).is_file():
                raise ADOSFileNotFoundError(
                    f"{rel}가 없습니다: {project_path / rel}",
                    location="OperationReportGenerator.create_operation_report",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        state = load_json(project_path / "workflow" / "workflow_state.json")
        final_quality = load_json(project_path / "reports" / "final_quality_report.json")
        checklist = load_json(project_path / "package" / "upload_readiness_checklist.json")
        readiness = load_json(project_path / "assets" / "asset_readiness_report.json")
        review = load_json(project_path / "reports" / "human_review_summary.json")
        run_report_path = project_path / "reports" / "run_report.json"
        run_report = load_json(run_report_path) if run_report_path.is_file() else None

        next_actions = []
        if readiness["missing_asset_types"]:
            next_actions.append(
                f"실제 자산 제작·등록: {', '.join(readiness['missing_asset_types'])}"
            )
        if not review["all_required_approved"]:
            next_actions.append(
                f"사람 검토 승인 필요: {review['pending_count']}건 대기, "
                f"{review['rejected_count']}건 반려"
            )
        if final_quality["final_decision"] != "PASS":
            next_actions.append("자산·검토 충족 후 FinalQualityGate 재실행")
        if not checklist["upload_ready"]:
            next_actions.append("upload_ready 충족 후 manual_upload_instructions에 따라 수동 업로드")

        report = {
            "project_id": project["project_id"],
            "topic": project["topic"]["title"],
            "operation_mode": "dummy_to_manual_handoff",
            "workflow_status": state["status"],
            "completed_stages": state["completed_stages"],
            "production_ready": final_quality["production_ready"],
            "upload_ready": final_quality["upload_ready"],
            "real_assets_present": readiness["real_assets_present"],
            "human_review_approved": review["all_required_approved"],
            "final_quality_decision": final_quality["final_decision"],
            "next_manual_actions": next_actions,
            "created_at": _now_iso(),
            "disclaimer": DISCLAIMER,
        }
        folder = project_path / REPORTS_DIR
        write_json(folder / REPORT_FILE, report)
        write_json(
            folder / "upload_preparation_report.json",
            {
                "project_id": project["project_id"],
                "operation_mode": "dummy_to_manual_handoff",
                "upload_ready": final_quality["upload_ready"],
                "upload_blockers": final_quality["upload_blockers"],
                "prepared_files": [rel for rel, _ in REQUIRED_INPUTS]
                + ["package/manual_upload_instructions.json"],
                "run_report_detected": run_report is not None,
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "handoff_report.json",
            {
                "project_id": project["project_id"],
                "handoff_to": "human_operator",
                "required_actions": next_actions,
                "references": {
                    "final_quality_report": "reports/final_quality_report.json",
                    "upload_checklist": "package/upload_readiness_checklist.json",
                    "manual_instructions": "package/manual_upload_instructions.json",
                    "asset_readiness": "assets/asset_readiness_report.json",
                },
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"운영 보고서 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"],
                          "upload_ready": final_quality["upload_ready"]},
            )
        return report

    def load_operation_report(self, project_path: str | Path) -> dict:
        path = self.report_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"operation_report.json이 없습니다: {path}",
                location="OperationReportGenerator.load_operation_report",
                suggested_fix="create_operation_report를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_operation_report(self, project_path: str | Path) -> bool:
        report = self.load_operation_report(project_path)
        ADOSValidator.require_fields(
            report, REPORT_REQUIRED_FIELDS,
            location="OperationReportGenerator.validate_operation_report",
        )
        return True
