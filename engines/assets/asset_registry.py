# -*- coding: utf-8 -*-
"""Asset registry (upload-preparation skeleton).

실제 제작 자산(영상/썸네일/음성/자막 등)의 요구사항과 등록 상태를 관리한다.
파일을 복사하지 않고 메타데이터만 기록한다. 자산 품질은 검증하지 않는다.
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
REQUIREMENTS_FILE = "asset_requirements.json"
MANIFEST_FILE = "production_asset_manifest.json"
READINESS_FILE = "asset_readiness_report.json"

SUPPORTED_ASSET_TYPES = ["image", "motion", "audio", "subtitle", "video", "thumbnail"]

ITEM_REQUIRED_FIELDS = [
    "asset_id",
    "asset_type",
    "file_path",
    "target_name",
    "exists",
    "metadata",
    "registered_at",
    "copied",
    "production_ready",
]

READINESS_DISCLAIMER = "Asset readiness report. Real asset quality was not verified."

# (plan 경로, asset_type, 개수 계산 함수)
_PLAN_SOURCES = [
    ("assets/images/visual_plan.json", "image",
     lambda plan: sum(sv["required_image_count"] for sv in plan["scene_visuals"])),
    ("assets/motion/motion_plan.json", "motion",
     lambda plan: len(plan["scene_motions"])),
    ("assets/audio/voice_plan.json", "audio",
     lambda plan: len(plan["narration_blocks"])),
    ("assets/subtitles/subtitle_plan.json", "subtitle",
     lambda plan: len(plan["target_languages"])),
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AssetRegistry:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def requirements_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / ASSETS_DIR / REQUIREMENTS_FILE

    def manifest_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / ASSETS_DIR / MANIFEST_FILE

    def readiness_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / ASSETS_DIR / READINESS_FILE

    def create_asset_requirements(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")

        expected_counts = {"video": 1, "thumbnail": 1}
        source_plans = []
        for rel, asset_type, count_fn in _PLAN_SOURCES:
            plan_path = project_path / rel
            if plan_path.is_file():
                expected_counts[asset_type] = count_fn(load_json(plan_path))
                source_plans.append(rel)
        for rel in ("timeline/timeline.json", "edit/editing_plan.json"):
            if (project_path / rel).is_file():
                source_plans.append(rel)

        requirements = {
            "project_id": project["project_id"],
            "topic": project["topic"]["title"],
            "required_asset_types": [
                t for t in SUPPORTED_ASSET_TYPES if expected_counts.get(t, 0) > 0
            ],
            "expected_counts": expected_counts,
            "source_plans": source_plans,
            "created_at": _now_iso(),
        }
        write_json(self.requirements_path(project_path), requirements)
        return requirements

    def create_production_asset_manifest(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        manifest = {
            "project_id": project["project_id"],
            "manifest_mode": "production",
            "assets": [],
            "production_ready": False,
            "created_at": _now_iso(),
        }
        write_json(self.manifest_path(project_path), manifest)
        return manifest

    def register_asset(
        self,
        project_path: str | Path,
        asset_type: str,
        file_path: str,
        target_name: str,
        metadata: dict | None = None,
    ) -> dict:
        project_path = Path(project_path)
        ADOSValidator.validate_enum(
            asset_type, SUPPORTED_ASSET_TYPES, field="asset_type",
            location="AssetRegistry.register_asset",
        )
        manifest = self.load_production_asset_manifest(project_path)
        item = {
            "asset_id": f"PA{len(manifest['assets']) + 1:03d}",
            "asset_type": asset_type,
            "file_path": str(file_path),
            "target_name": target_name,
            "exists": Path(file_path).is_file(),
            "metadata": metadata or {},
            "registered_at": _now_iso(),
            "copied": False,  # 메타데이터 기록만 — 파일 복사 없음
            "production_ready": False,
        }
        manifest["assets"].append(item)
        write_json(self.manifest_path(project_path), manifest)
        if self.logger:
            self.logger.info(
                f"제작 자산 등록: {item['asset_id']} ({asset_type}, exists={item['exists']})",
                metadata={"asset_id": item["asset_id"], "asset_type": asset_type},
            )
        return item

    def load_production_asset_manifest(self, project_path: str | Path) -> dict:
        path = self.manifest_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"production_asset_manifest.json이 없습니다: {path}",
                location="AssetRegistry.load_production_asset_manifest",
                suggested_fix="create_production_asset_manifest를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_production_asset_manifest(self, project_path: str | Path) -> bool:
        manifest = self.load_production_asset_manifest(project_path)
        loc = "AssetRegistry.validate_production_asset_manifest"
        ADOSValidator.require_fields(
            manifest, ["project_id", "manifest_mode", "assets"], location=loc
        )
        for item in manifest["assets"]:
            ADOSValidator.require_fields(item, ITEM_REQUIRED_FIELDS, location=loc)
            ADOSValidator.validate_enum(
                item["asset_type"], SUPPORTED_ASSET_TYPES,
                field="asset_type", location=loc,
            )
        return True

    def create_asset_readiness_report(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        if not self.requirements_path(project_path).is_file():
            raise ADOSFileNotFoundError(
                f"asset_requirements.json이 없습니다: {self.requirements_path(project_path)}",
                location="AssetRegistry.create_asset_readiness_report",
                suggested_fix="create_asset_requirements를 먼저 실행하세요.",
            )
        requirements = load_json(self.requirements_path(project_path))
        manifest = self.load_production_asset_manifest(project_path)

        registered_counts = {t: 0 for t in requirements["required_asset_types"]}
        for item in manifest["assets"]:
            if item["exists"] and item["asset_type"] in registered_counts:
                registered_counts[item["asset_type"]] += 1
        missing = [t for t, n in registered_counts.items() if n == 0]

        report = {
            "project_id": requirements["project_id"],
            "required_asset_types": requirements["required_asset_types"],
            "registered_counts": registered_counts,
            "missing_asset_types": missing,
            "real_assets_present": len(missing) == 0,
            "production_ready": False,
            "disclaimer": READINESS_DISCLAIMER,
            "created_at": _now_iso(),
        }
        write_json(self.readiness_path(project_path), report)
        return report
