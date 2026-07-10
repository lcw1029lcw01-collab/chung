# -*- coding: utf-8 -*-
"""Provider importer (v0.2 — manual integration preparation).

외부에서 수동 생성된 자산을 메타데이터로만 가져오고,
기존 AssetRegistry에 연결한다. 파일 복사는 하지 않는다.
upload_ready는 여기서 절대 변경하지 않는다.
근거: docs/32_PROVIDER_INTEGRATION_V0_2.md #9
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
from engines.assets import AssetRegistry
from engines.assets.asset_registry import SUPPORTED_ASSET_TYPES

from .provider_job_manager import SUPPORTED_PROVIDERS

IMPORTS_DIR = Path("providers") / "imports"
MANIFEST_FILE = "provider_import_manifest.json"

ITEM_REQUIRED_FIELDS = [
    "import_id",
    "provider_name",
    "asset_type",
    "file_path",
    "target_name",
    "metadata",
    "exists",
    "linked_to_asset_registry",
    "imported_at",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProviderImporter:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger
        self.registry = AssetRegistry(logger)

    def manifest_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / IMPORTS_DIR / MANIFEST_FILE

    def _load_or_create_manifest(self, project_path: Path) -> dict:
        path = self.manifest_path(project_path)
        if path.is_file():
            return load_json(path)
        project = load_json(project_path / "project.json")
        return {
            "project_id": project["project_id"],
            "import_mode": "manual",
            "external_call_made": False,
            "imports": [],
            "created_at": _now_iso(),
        }

    def import_provider_asset_metadata(
        self,
        project_path: str | Path,
        provider_name: str,
        asset_type: str,
        file_path: str,
        target_name: str,
        job_id: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        project_path = Path(project_path)
        loc = "ProviderImporter.import_provider_asset_metadata"
        ADOSValidator.validate_enum(
            provider_name, SUPPORTED_PROVIDERS, field="provider_name", location=loc
        )
        ADOSValidator.validate_enum(
            asset_type, SUPPORTED_ASSET_TYPES, field="asset_type", location=loc
        )
        manifest = self._load_or_create_manifest(project_path)
        item = {
            "import_id": f"PI{len(manifest['imports']) + 1:03d}",
            "provider_name": provider_name,
            "asset_type": asset_type,
            "file_path": str(file_path),
            "target_name": target_name,
            "job_id": job_id,
            "metadata": metadata or {},
            "exists": Path(file_path).is_file(),
            "linked_to_asset_registry": False,
            "asset_registry_id": None,
            "imported_at": _now_iso(),
        }
        manifest["imports"].append(item)
        write_json(self.manifest_path(project_path), manifest)
        if self.logger:
            self.logger.info(
                f"provider 자산 import: {item['import_id']} ({provider_name}/{asset_type})",
                metadata={"import_id": item["import_id"], "provider": provider_name},
            )
        return item

    def link_import_to_asset_registry(
        self, project_path: str | Path, import_id: str
    ) -> dict:
        project_path = Path(project_path)
        manifest = self.load_provider_import_manifest(project_path)
        for item in manifest["imports"]:
            if item["import_id"] == import_id:
                registered = self.registry.register_asset(
                    project_path,
                    item["asset_type"],
                    item["file_path"],
                    item["target_name"],
                    metadata={
                        **item["metadata"],
                        "provider_name": item["provider_name"],
                        "import_id": import_id,
                        "job_id": item["job_id"],
                    },
                )
                item["linked_to_asset_registry"] = True
                item["asset_registry_id"] = registered["asset_id"]
                write_json(self.manifest_path(project_path), manifest)
                if self.logger:
                    self.logger.info(
                        f"import → registry 연결: {import_id} → {registered['asset_id']}",
                        metadata={"import_id": import_id,
                                  "asset_id": registered["asset_id"]},
                    )
                return item
        raise ADOSFileNotFoundError(
            f"import를 찾을 수 없습니다: {import_id}",
            location="ProviderImporter.link_import_to_asset_registry",
            suggested_fix="provider_import_manifest.json의 import_id를 확인하세요.",
        )

    def load_provider_import_manifest(self, project_path: str | Path) -> dict:
        path = self.manifest_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"provider_import_manifest.json이 없습니다: {path}",
                location="ProviderImporter.load_provider_import_manifest",
                suggested_fix="import_provider_asset_metadata를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_provider_import_manifest(self, project_path: str | Path) -> bool:
        manifest = self.load_provider_import_manifest(project_path)
        loc = "ProviderImporter.validate_provider_import_manifest"
        ADOSValidator.require_fields(
            manifest, ["project_id", "import_mode", "imports"], location=loc
        )
        for item in manifest["imports"]:
            ADOSValidator.require_fields(item, ITEM_REQUIRED_FIELDS, location=loc)
            ADOSValidator.validate_enum(
                item["provider_name"], SUPPORTED_PROVIDERS,
                field="provider_name", location=loc,
            )
            ADOSValidator.validate_enum(
                item["asset_type"], SUPPORTED_ASSET_TYPES,
                field="asset_type", location=loc,
            )
        return True
