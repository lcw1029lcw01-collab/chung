# -*- coding: utf-8 -*-
"""Manual production loop (v0.2 — manual production loop).

수동 워크스페이스 준비 → 사람 배치 파일의 메타데이터 등록 →
사람 검토 → 최종 게이트·업로드 준비 재실행까지의 폐루프를 관장한다.

주의: 파일 복사·업로드·외부 호출은 없다. upload_ready는 오직
FinalQualityGate 재실행 결과로만 갱신되며 강제로 true로 만들지 않는다.
근거: docs/33_MANUAL_PRODUCTION_LOOP_V0_2.md
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    load_json,
    write_json,
)
from engines.assets import AssetRegistry
from engines.final_quality import FinalQualityGate
from engines.provider_jobs import ProviderImporter
from engines.provider_jobs.provider_job_manager import SUPPORTED_PROVIDERS
from engines.reporting import OperationReportGenerator
from engines.review import HumanReviewEngine
from engines.review.human_review_engine import DEFAULT_CHECKPOINTS
from engines.upload import UploadPreparer

from .manual_intake_manager import STATUS_REGISTERED, ManualIntakeManager
from .manual_workspace_manager import ManualWorkspaceManager

REPORTS_DIR = "reports"
LOOP_REPORT_FILE = "manual_production_loop_report.json"

LOOP_REPORT_DISCLAIMER = (
    "Manual production loop report. No upload was performed."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ManualProductionLoop:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger
        self.workspaces = ManualWorkspaceManager(logger)
        self.intake = ManualIntakeManager(logger)
        self.registry = AssetRegistry(logger)
        self.importer = ProviderImporter(logger)
        self.reviews = HumanReviewEngine(logger)
        self.final_gate = FinalQualityGate(logger)
        self.preparer = UploadPreparer(logger)

    def loop_report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / LOOP_REPORT_FILE

    def prepare_manual_loop(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")

        if not self.registry.requirements_path(project_path).is_file():
            self.registry.create_asset_requirements(project_path)
        if not self.registry.manifest_path(project_path).is_file():
            self.registry.create_production_asset_manifest(project_path)

        workspace_info = self.workspaces.create_manual_workspace(project_path)
        intake_manifest = self.intake.create_asset_intake_manifest(project_path)

        if not self.reviews.checkpoints_path(project_path).is_file():
            self.reviews.create_review_checkpoints(project_path)

        summary = {
            "project_id": project["project_id"],
            "workspace_path": workspace_info["workspace_path"],
            "intake_manifest_path": str(self.intake.manifest_path(project_path)),
            "intake_item_count": len(intake_manifest["items"]),
            "upload_ready": False,
            "created_at": _now_iso(),
        }
        if self.logger:
            self.logger.info(
                f"수동 제작 루프 준비 완료: {summary['intake_item_count']} items",
                metadata={"project_id": project["project_id"]},
            )
        return summary

    def import_ready_assets(self, project_path: str | Path) -> int:
        """actual_file_path가 기록된 intake item을 메타데이터로만 등록한다.

        provider_hint가 지원 provider면 ProviderImporter를 거쳐 등록하고,
        아니면 AssetRegistry에 직접 등록한다. 파일 복사·업로드는 없다.
        """
        project_path = Path(project_path)
        manifest = self.intake.load_asset_intake_manifest(project_path)
        registered = 0
        for item in manifest["items"]:
            if not item["actual_file_path"] or item["status"] == STATUS_REGISTERED:
                continue
            target_name = Path(item["actual_file_path"]).name
            metadata = {
                "intake_item_id": item["item_id"],
                "source_stage": item["source_stage"],
                "registered_by": "manual_production_loop",
            }
            if item["provider_hint"] in SUPPORTED_PROVIDERS:
                imported = self.importer.import_provider_asset_metadata(
                    project_path, item["provider_hint"], item["asset_type"],
                    item["actual_file_path"], target_name, metadata=metadata,
                )
                linked = self.importer.link_import_to_asset_registry(
                    project_path, imported["import_id"]
                )
                asset_id = linked["asset_registry_id"]
            else:
                asset = self.registry.register_asset(
                    project_path, item["asset_type"],
                    item["actual_file_path"], target_name, metadata=metadata,
                )
                asset_id = asset["asset_id"]
            item["status"] = STATUS_REGISTERED
            item["notes"] = f"registered as {asset_id}"
            registered += 1
        if registered:
            write_json(self.intake.manifest_path(project_path), manifest)
        if self.logger:
            self.logger.info(
                f"intake 자산 등록 완료: {registered}건 (메타데이터만, 복사 없음)",
                metadata={"registered": registered},
            )
        return registered

    def approve_required_reviews(
        self,
        project_path: str | Path,
        reviewer: str = "human",
        notes: str | None = None,
    ) -> dict:
        """기본 체크포인트 전체를 승인한다. 명시적으로 호출할 때만 실행된다."""
        project_path = Path(project_path)
        summary = None
        for checkpoint_id, _stage in DEFAULT_CHECKPOINTS:
            summary = self.reviews.approve_checkpoint(
                project_path, checkpoint_id, reviewer=reviewer, notes=notes
            )
        return summary

    def rerun_final_readiness(self, project_path: str | Path) -> bool:
        project_path = Path(project_path)
        self.registry.create_asset_readiness_report(project_path)
        final_report = self.final_gate.create_final_quality_report(project_path)
        self.preparer.create_youtube_metadata_package(project_path)
        self.preparer.create_upload_readiness_checklist(project_path)
        self.preparer.create_manual_upload_instructions(project_path)
        OperationReportGenerator(self.logger).create_operation_report(project_path)
        return bool(final_report["upload_ready"])

    def create_manual_loop_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        gate_path = project_path / REPORTS_DIR / "final_upload_gate.json"
        if not gate_path.is_file():
            raise ADOSFileNotFoundError(
                f"final_upload_gate.json이 없습니다: {gate_path}",
                location="ManualProductionLoop.create_manual_loop_report",
                suggested_fix="rerun_final_readiness를 먼저 실행하세요.",
            )
        gate = load_json(gate_path)
        intake_manifest = self.intake.load_asset_intake_manifest(project_path)
        review_summary = self.reviews.load_review_summary(project_path)

        report = {
            "project_id": project["project_id"],
            "workspace_path": intake_manifest["workspace_path"],
            "intake_manifest_path": str(self.intake.manifest_path(project_path)),
            "registered_asset_count": sum(
                1 for i in intake_manifest["items"]
                if i["status"] == STATUS_REGISTERED
            ),
            "human_review_status": {
                "all_required_approved": review_summary["all_required_approved"],
                "approved_count": review_summary["approved_count"],
                "pending_count": review_summary["pending_count"],
                "rejected_count": review_summary["rejected_count"],
            },
            "final_quality_decision": gate["gate_result"],
            "upload_ready": bool(gate["upload_ready"]),
            "blockers": gate["blockers"],
            "created_at": _now_iso(),
            "disclaimer": LOOP_REPORT_DISCLAIMER,
        }
        write_json(self.loop_report_path(project_path), report)
        if self.logger:
            self.logger.info(
                f"수동 제작 루프 보고서 생성: upload_ready={report['upload_ready']}",
                metadata={"project_id": project["project_id"]},
            )
        return report
