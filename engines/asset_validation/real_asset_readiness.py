# -*- coding: utf-8 -*-
"""Real asset readiness (v0.3 — real manual trial preparation).

등록 자산의 파일 검증 결과를 종합해 실자산 준비도를 판정한다.
production_ready_candidate는 참고 지표이며 기존 게이트를 대체하지 않는다.
근거: docs/34_REAL_MANUAL_TRIAL_V0_3.md #9, #11
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

ASSETS_DIR = "assets"
READINESS_REPORT_FILE = "real_asset_readiness_report.json"

REQUIRED_INPUTS = [
    ("assets/production_asset_manifest.json",
     "AssetRegistry.create_production_asset_manifest"),
    ("assets/asset_requirements.json", "AssetRegistry.create_asset_requirements"),
    ("assets/asset_file_validation_report.json",
     "AssetFileValidator.validate_registered_assets"),
]

REPORT_REQUIRED_FIELDS = [
    "project_id",
    "required_asset_types",
    "registered_counts",
    "valid_counts",
    "missing_asset_types",
    "invalid_assets",
    "real_assets_present",
    "real_final_video_present",
    "production_ready_candidate",
    "created_at",
    "disclaimer",
]

READINESS_DISCLAIMER = (
    "Real asset readiness checks file existence, extension, and size only. "
    "It does not verify media quality."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RealAssetReadiness:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / ASSETS_DIR / READINESS_REPORT_FILE

    def create_real_asset_readiness_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for rel, fix in REQUIRED_INPUTS:
            if not (project_path / rel).is_file():
                raise ADOSFileNotFoundError(
                    f"{rel}가 없습니다: {project_path / rel}",
                    location="RealAssetReadiness.create_real_asset_readiness_report",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        manifest = load_json(project_path / "assets" / "production_asset_manifest.json")
        requirements = load_json(project_path / "assets" / "asset_requirements.json")
        validation = load_json(
            project_path / "assets" / "asset_file_validation_report.json"
        )

        required_types = requirements["required_asset_types"]
        validation_by_asset = {i["asset_id"]: i for i in validation["items"]}

        registered_counts = {t: 0 for t in required_types}
        valid_counts = {t: 0 for t in required_types}
        invalid_assets = []
        for asset in manifest["assets"]:
            asset_type = asset["asset_type"]
            if asset_type in registered_counts:
                registered_counts[asset_type] += 1
            item = validation_by_asset.get(asset["asset_id"])
            if item is None or item["validation_status"] != "PASS":
                invalid_assets.append({
                    "asset_id": asset["asset_id"],
                    "asset_type": asset_type,
                    "issues": item["issues"] if item else ["not_validated"],
                })
            elif asset_type in valid_counts:
                valid_counts[asset_type] += 1

        missing = [t for t in required_types if valid_counts[t] == 0]
        real_assets_present = len(missing) == 0
        real_final_video_present = valid_counts.get("video", 0) > 0
        production_ready_candidate = (
            real_assets_present
            and real_final_video_present
            and len(invalid_assets) == 0
        )

        report = {
            "project_id": requirements["project_id"],
            "required_asset_types": required_types,
            "registered_counts": registered_counts,
            "valid_counts": valid_counts,
            "missing_asset_types": missing,
            "invalid_assets": invalid_assets,
            "real_assets_present": real_assets_present,
            "real_final_video_present": real_final_video_present,
            "production_ready_candidate": production_ready_candidate,
            "created_at": _now_iso(),
            "disclaimer": READINESS_DISCLAIMER,
        }
        write_json(self.report_path(project_path), report)
        if self.logger:
            self.logger.info(
                f"실자산 준비도: candidate={production_ready_candidate}, "
                f"missing={missing}",
                metadata={"project_id": report["project_id"]},
            )
        return report

    def load_real_asset_readiness_report(self, project_path: str | Path) -> dict:
        path = self.report_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"real_asset_readiness_report.json이 없습니다: {path}",
                location="RealAssetReadiness.load_real_asset_readiness_report",
                suggested_fix="create_real_asset_readiness_report를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_real_asset_readiness_report(self, project_path: str | Path) -> bool:
        report = self.load_real_asset_readiness_report(project_path)
        ADOSValidator.require_fields(
            report, REPORT_REQUIRED_FIELDS,
            location="RealAssetReadiness.validate_real_asset_readiness_report",
        )
        return True
