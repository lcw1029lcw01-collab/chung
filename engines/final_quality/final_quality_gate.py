# -*- coding: utf-8 -*-
"""Final quality gate (upload-preparation skeleton).

기본 품질 게이트 + 실자산 준비 + 사람 검토 + 실제 최종 영상 존재를
종합해 업로드 가능 여부를 판정한다.

주의: 실제 영상 품질을 검증하지 않는다. 일반적인 dummy 파이프라인에서는
BLOCKED가 정상 결과다. PASS를 강제하지 않는다.
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
REPORT_FILE = "final_quality_report.json"
GATE_FILE = "final_upload_gate.json"

REQUIRED_INPUTS = [
    ("reports/quality_report.json", "QualityEngine.create_dummy_quality_report"),
    ("reports/quality_gate.json", "QualityEngine.create_dummy_quality_report"),
    ("edit/editing_plan.json", "EditingEngine.create_dummy_editing_plan"),
    ("assets/asset_readiness_report.json", "AssetRegistry.create_asset_readiness_report"),
    ("reports/human_review_summary.json", "HumanReviewEngine.create_review_checkpoints"),
]

REPORT_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "final_quality_mode",
    "base_quality_gate_result",
    "asset_readiness",
    "human_review_status",
    "real_video_present",
    "final_score",
    "final_decision",
    "upload_blockers",
    "production_ready",
    "upload_ready",
    "created_at",
    "disclaimer",
]

DISCLAIMER = "Final quality gate. This does not verify real video quality."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FinalQualityGate:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / REPORT_FILE

    def gate_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / GATE_FILE

    def create_final_quality_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for rel, fix in REQUIRED_INPUTS:
            if not (project_path / rel).is_file():
                raise ADOSFileNotFoundError(
                    f"{rel}가 없습니다: {project_path / rel}",
                    location="FinalQualityGate.create_final_quality_report",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        quality_report = load_json(project_path / "reports" / "quality_report.json")
        quality_gate = load_json(project_path / "reports" / "quality_gate.json")
        readiness = load_json(project_path / "assets" / "asset_readiness_report.json")
        review = load_json(project_path / "reports" / "human_review_summary.json")

        # 실제 최종 영상 자산 존재 여부 (production manifest 기준)
        real_video_present = False
        manifest_path = project_path / "assets" / "production_asset_manifest.json"
        if manifest_path.is_file():
            manifest = load_json(manifest_path)
            real_video_present = any(
                a["asset_type"] == "video" and a["exists"] for a in manifest["assets"]
            )

        blockers = []
        if quality_gate["gate_result"] != "PASS":
            blockers.append("quality_gate_not_pass")
        if not readiness["real_assets_present"]:
            blockers.append("real_assets_missing")
        if not review["upload_allowed_by_human_review"]:
            blockers.append("human_review_not_approved")
        if not real_video_present:
            blockers.append("real_final_video_missing")

        final_decision = "PASS" if not blockers else "BLOCKED"
        upload_ready = final_decision == "PASS"

        report = {
            "project_id": project["project_id"],
            "topic": project["topic"]["title"],
            "final_quality_mode": "readiness_check",
            "base_quality_gate_result": quality_gate["gate_result"],
            "asset_readiness": {
                "real_assets_present": readiness["real_assets_present"],
                "missing_asset_types": readiness["missing_asset_types"],
            },
            "human_review_status": {
                "all_required_approved": review["all_required_approved"],
                "approved_count": review["approved_count"],
                "pending_count": review["pending_count"],
                "rejected_count": review["rejected_count"],
            },
            "real_video_present": real_video_present,
            "final_score": quality_report["total_score"],
            "final_decision": final_decision,
            "upload_blockers": blockers,
            "production_ready": upload_ready,
            "upload_ready": upload_ready,
            "created_at": _now_iso(),
            "disclaimer": DISCLAIMER,
        }
        write_json(self.report_path(project_path), report)
        write_json(
            self.gate_path(project_path),
            {
                "project_id": project["project_id"],
                "gate_result": final_decision,
                "upload_ready": upload_ready,
                "blockers": blockers,
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"최종 품질 게이트: {final_decision}",
                metadata={"project_id": project["project_id"], "blockers": blockers},
            )
        return report

    def load_final_quality_report(self, project_path: str | Path) -> dict:
        path = self.report_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"final_quality_report.json이 없습니다: {path}",
                location="FinalQualityGate.load_final_quality_report",
                suggested_fix="create_final_quality_report를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_final_quality_report(self, project_path: str | Path) -> bool:
        report = self.load_final_quality_report(project_path)
        ADOSValidator.require_fields(
            report, REPORT_REQUIRED_FIELDS,
            location="FinalQualityGate.validate_final_quality_report",
        )
        return True
