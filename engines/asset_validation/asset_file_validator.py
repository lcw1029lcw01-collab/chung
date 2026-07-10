# -*- coding: utf-8 -*-
"""Asset file validator (v0.3 — real manual trial preparation).

사람이 배치한 실제 파일을 존재/확장자/최소 크기로만 검증한다.
미디어 내용은 검사하지 않는다 (ffmpeg 없음). 업로드·외부 호출 없음.
근거: docs/34_REAL_MANUAL_TRIAL_V0_3.md #9
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSLogger,
    ADOSPathManager,
    ADOSValidator,
    load_json,
    load_yaml,
    write_json,
)
from engines.assets import AssetRegistry
from engines.assets.asset_registry import SUPPORTED_ASSET_TYPES

ASSETS_DIR = "assets"
VALIDATION_REPORT_FILE = "asset_file_validation_report.json"

# config/asset_validation.yaml과 동일한 안전 기본값 (config 없으면 이 값 사용)
DEFAULT_VALIDATION_CONFIG = {
    "allow_upload": False,
    "allow_external_calls": False,
    "minimum_file_sizes": {
        "image": 1024,
        "motion": 1024,
        "audio": 1024,
        "subtitle": 1,
        "video": 1024,
        "thumbnail": 1024,
    },
    "allowed_extensions": {
        "image": [".png", ".jpg", ".jpeg", ".webp"],
        "motion": [".mp4", ".mov", ".webm"],
        "audio": [".mp3", ".wav", ".m4a"],
        "subtitle": [".srt", ".vtt", ".json"],
        "video": [".mp4", ".mov"],
        "thumbnail": [".png", ".jpg", ".jpeg", ".webp"],
    },
}

VALIDATION_DISCLAIMER = (
    "Asset file validation checks file existence, extension, and size only. "
    "It does not verify media content or quality."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AssetFileValidator:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def report_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / ASSETS_DIR / VALIDATION_REPORT_FILE

    def load_validation_config(self, start: str | Path | None = None) -> dict:
        """config/asset_validation.yaml을 읽는다. 없으면 안전 기본값을 쓴다."""
        try:
            root = ADOSPathManager.find_project_root(start)
        except Exception:
            return dict(DEFAULT_VALIDATION_CONFIG)
        config_path = root / "config" / "asset_validation.yaml"
        if not config_path.is_file():
            return dict(DEFAULT_VALIDATION_CONFIG)
        config = load_yaml(config_path)
        merged = dict(DEFAULT_VALIDATION_CONFIG)
        if isinstance(config, dict):
            merged.update(config)
        return merged

    def validate_file(
        self,
        file_path: str | Path,
        asset_type: str,
        config: dict | None = None,
    ) -> dict:
        """단일 파일을 존재/확장자/크기로 검증한 결과 dict를 돌려준다."""
        ADOSValidator.validate_enum(
            asset_type, SUPPORTED_ASSET_TYPES, field="asset_type",
            location="AssetFileValidator.validate_file",
        )
        config = config or self.load_validation_config()
        path = Path(file_path)
        extension = path.suffix.lower()
        allowed = [e.lower() for e in config["allowed_extensions"][asset_type]]
        minimum = int(config["minimum_file_sizes"][asset_type])

        exists = path.is_file()
        extension_allowed = extension in allowed
        size_bytes = path.stat().st_size if exists else 0
        size_ok = exists and size_bytes >= minimum

        issues = []
        if not exists:
            issues.append("file_missing")
        if not extension_allowed:
            issues.append(f"extension_not_allowed: {extension or '(none)'}")
        if exists and not size_ok:
            issues.append(f"file_too_small: {size_bytes} < {minimum}")

        return {
            "asset_type": asset_type,
            "file_path": str(file_path),
            "exists": exists,
            "extension": extension,
            "extension_allowed": extension_allowed,
            "size_bytes": size_bytes,
            "minimum_size_bytes": minimum,
            "size_ok": size_ok,
            "validation_status": "PASS" if not issues else "FAIL",
            "issues": issues,
        }

    def validate_registered_assets(self, project_path: str | Path) -> dict:
        """production manifest의 등록 자산 전체를 검증하고 보고서를 쓴다."""
        project_path = Path(project_path)
        manifest = AssetRegistry(self.logger).load_production_asset_manifest(
            project_path
        )
        config = self.load_validation_config(project_path)

        items = []
        for asset in manifest["assets"]:
            result = self.validate_file(
                asset["file_path"], asset["asset_type"], config=config
            )
            items.append({"asset_id": asset["asset_id"], **result})

        pass_count = sum(1 for i in items if i["validation_status"] == "PASS")
        report = {
            "project_id": manifest["project_id"],
            "validation_mode": "existence_extension_size_only",
            "items": items,
            "pass_count": pass_count,
            "fail_count": len(items) - pass_count,
            "created_at": _now_iso(),
            "disclaimer": VALIDATION_DISCLAIMER,
        }
        write_json(self.report_path(project_path), report)
        if self.logger:
            self.logger.info(
                f"자산 파일 검증: PASS {pass_count} / FAIL {len(items) - pass_count}",
                metadata={"project_id": manifest["project_id"]},
            )
        return report

    def load_validation_report(self, project_path: str | Path) -> dict:
        return load_json(self.report_path(project_path))
