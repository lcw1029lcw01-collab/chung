# -*- coding: utf-8 -*-
"""Manual asset importer (walking skeleton).

사용자가 수동으로 만든 자산(이미지/영상/음성/자막 등)을 프로젝트에
메타데이터로만 등록한다. 파일 복사는 하지 않는다 (copied: false).
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
MANIFEST_FILE = "manual_asset_manifest.json"
PLAN_FILE = "manual_asset_import_plan.json"

SUPPORTED_ASSET_TYPES = ["image", "motion", "audio", "subtitle", "video", "thumbnail"]

ITEM_REQUIRED_FIELDS = [
    "asset_id",
    "asset_type",
    "source_path",
    "target_name",
    "metadata",
    "registered_at",
    "copied",
    "production_ready",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ManualAssetImporter:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def manifest_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / ASSETS_DIR / MANIFEST_FILE

    def plan_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / ASSETS_DIR / PLAN_FILE

    def create_import_plan(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        plan = {
            "project_id": project["project_id"],
            "import_mode": "manual",
            "supported_asset_types": SUPPORTED_ASSET_TYPES,
            "instructions": [
                "수동으로 생성한 자산을 register_manual_asset으로 등록한다.",
                "현재는 메타데이터 기록만 하며 파일을 복사하지 않는다 (copied: false).",
            ],
            "created_at": _now_iso(),
        }
        write_json(self.plan_path(project_path), plan)
        if not self.manifest_path(project_path).is_file():
            write_json(
                self.manifest_path(project_path),
                {
                    "project_id": project["project_id"],
                    "import_mode": "manual",
                    "assets": [],
                    "created_at": _now_iso(),
                },
            )
        return plan

    def register_manual_asset(
        self,
        project_path: str | Path,
        asset_type: str,
        source_path: str,
        target_name: str,
        metadata: dict | None = None,
    ) -> dict:
        project_path = Path(project_path)
        ADOSValidator.validate_enum(
            asset_type, SUPPORTED_ASSET_TYPES, field="asset_type",
            location="ManualAssetImporter.register_manual_asset",
        )
        if not self.manifest_path(project_path).is_file():
            self.create_import_plan(project_path)
        manifest = load_json(self.manifest_path(project_path))

        item = {
            "asset_id": f"MA{len(manifest['assets']) + 1:03d}",
            "asset_type": asset_type,
            "source_path": str(source_path),
            "target_name": target_name,
            "metadata": metadata or {},
            "registered_at": _now_iso(),
            "copied": False,  # 메타데이터 기록만 — 파일 복사 없음
            "production_ready": False,
        }
        manifest["assets"].append(item)
        write_json(self.manifest_path(project_path), manifest)
        if self.logger:
            self.logger.info(
                f"수동 자산 등록: {item['asset_id']} ({asset_type})",
                metadata={"asset_id": item["asset_id"], "asset_type": asset_type},
            )
        return item

    def load_manual_asset_manifest(self, project_path: str | Path) -> dict:
        path = self.manifest_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"manual_asset_manifest.json이 없습니다: {path}",
                location="ManualAssetImporter.load_manual_asset_manifest",
                suggested_fix="create_import_plan을 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_manual_asset_manifest(self, project_path: str | Path) -> bool:
        manifest = self.load_manual_asset_manifest(project_path)
        loc = "ManualAssetImporter.validate_manual_asset_manifest"
        ADOSValidator.require_fields(
            manifest, ["project_id", "import_mode", "assets"], location=loc
        )
        for item in manifest["assets"]:
            ADOSValidator.require_fields(item, ITEM_REQUIRED_FIELDS, location=loc)
            ADOSValidator.validate_enum(
                item["asset_type"], SUPPORTED_ASSET_TYPES,
                field="asset_type", location=loc,
            )
        return True
