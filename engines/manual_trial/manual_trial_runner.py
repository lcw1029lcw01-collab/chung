# -*- coding: utf-8 -*-
"""Manual trial runner (v0.3 — real manual trial preparation).

준비 → (사람 파일 배치) → 검증 → 검토 승인 → 최종화의 트라이얼 흐름을
관장한다. 외부 호출·업로드·실미디어 생성은 없다.
upload_ready는 기존 게이트 규칙이 실제로 통과할 때만 true가 된다.
근거: docs/34_REAL_MANUAL_TRIAL_V0_3.md #5
"""
from pathlib import Path

from core import ADOSLogger, ADOSPathManager, load_json
from engines.asset_validation import AssetFileValidator, RealAssetReadiness
from engines.manual_production import ManualProductionLoop
from engines.pipeline import FullPipelineRunner
from engines.provider_jobs import ProviderExporter

from .manual_trial_guide import ManualTrialGuide


class ManualTrialRunner:
    def __init__(
        self,
        path_manager: ADOSPathManager | None = None,
        logger: ADOSLogger | None = None,
    ):
        self.logger = logger
        self.pipeline = FullPipelineRunner(path_manager, logger)
        self.exporter = ProviderExporter(logger)
        self.loop = ManualProductionLoop(logger)
        self.guide = ManualTrialGuide(logger)
        self.validator = AssetFileValidator(logger)
        self.readiness = RealAssetReadiness(logger)

    def prepare_real_manual_trial(self) -> dict:
        """전체 dummy 파이프라인 + 업로드 준비 + 트라이얼 준비물 일체를 만든다.

        검토는 자동 승인하지 않는다. upload_ready는 false가 정상이다.
        """
        summary = self.pipeline.run_full_dummy_pipeline_with_upload_preparation()
        project_path = Path(summary["project_path"])

        export_summary = self.exporter.export_all_provider_packs(project_path)
        loop_prep = self.loop.prepare_manual_loop(project_path)
        guide = self.guide.create_trial_guide(project_path)

        return {
            "project_id": summary["project_id"],
            "project_path": str(project_path),
            "workspace_path": loop_prep["workspace_path"],
            "trial_guide_path": str(self.guide.guide_path(project_path)),
            "trial_checklist_path": str(self.guide.checklist_path(project_path)),
            "trial_guide_md_path": str(self.guide.guide_md_path(project_path)),
            "intake_manifest_path": loop_prep["intake_manifest_path"],
            "provider_export_paths": export_summary["exports"],
            "expected_asset_file_count": len(guide["expected_asset_files"]),
            "upload_ready": summary["upload_preparation"]["upload_ready"],
            "next_human_action": (
                "가이드의 기대 경로에 실제 파일을 배치하고 intake manifest에 "
                "actual_file_path를 기록한 뒤 validate 스크립트를 실행하세요."
            ),
        }

    def validate_real_manual_trial(self, project_path: str | Path) -> dict:
        """사람이 배치한 파일을 등록·검증하고 준비도·게이트를 재계산한다."""
        project_path = Path(project_path)
        registered = self.loop.import_ready_assets(project_path)
        validation = self.validator.validate_registered_assets(project_path)
        readiness = self.readiness.create_real_asset_readiness_report(project_path)
        # 최종 게이트·업로드 준비·운영 보고서 재실행 (upload_ready 강제 없음)
        upload_ready = self.loop.rerun_final_readiness(project_path)
        gate = load_json(project_path / "reports" / "final_upload_gate.json")

        return {
            "project_id": readiness["project_id"],
            "registered_this_run": registered,
            "validation_pass_count": validation["pass_count"],
            "validation_fail_count": validation["fail_count"],
            "real_assets_present": readiness["real_assets_present"],
            "real_final_video_present": readiness["real_final_video_present"],
            "production_ready_candidate": readiness["production_ready_candidate"],
            "upload_ready": upload_ready,
            "blockers": gate["blockers"],
            "asset_file_validation_report": str(
                self.validator.report_path(project_path)
            ),
            "real_asset_readiness_report": str(
                self.readiness.report_path(project_path)
            ),
            "final_quality_report": str(
                self.loop.final_gate.report_path(project_path)
            ),
        }

    def approve_real_manual_trial_reviews(
        self,
        project_path: str | Path,
        reviewer: str = "human",
        notes: str | None = None,
    ) -> dict:
        """검토 체크포인트 전체 승인 — 명시적으로 호출할 때만 실행된다."""
        return self.loop.approve_required_reviews(project_path, reviewer, notes)

    def finalize_real_manual_trial(self, project_path: str | Path) -> bool:
        """검증·준비도·게이트·업로드 패키지 전체를 재실행하고 판정을 돌려준다."""
        project_path = Path(project_path)
        self.validator.validate_registered_assets(project_path)
        self.readiness.create_real_asset_readiness_report(project_path)
        # 게이트 → 메타데이터 패키지 → 체크리스트 → 수동 안내 → 운영 보고서
        return self.loop.rerun_final_readiness(project_path)
