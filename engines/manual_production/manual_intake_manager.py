# -*- coding: utf-8 -*-
"""Manual intake manager (v0.2 — manual production loop).

사람이 외부에서 생성해 와야 하는 자산 목록(intake manifest)을 만든다.
asset requirements·각종 plan·export pack이 있으면 그것을 근거로 item을
세분화한다. 파일 복사·업로드는 하지 않는다.
근거: docs/33_MANUAL_PRODUCTION_LOOP_V0_2.md #6
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSValidationError,
    ADOSValidator,
    load_json,
    write_json,
)
from engines.assets.asset_registry import SUPPORTED_ASSET_TYPES

from .manual_workspace_manager import ManualWorkspaceManager

MANIFEST_FILE = "asset_intake_manifest.json"

STATUS_WAITING = "WAITING_FOR_HUMAN"
STATUS_ASSIGNED = "FILE_ASSIGNED"
STATUS_REGISTERED = "REGISTERED"

ITEM_REQUIRED_FIELDS = [
    "item_id",
    "asset_type",
    "source_stage",
    "provider_hint",
    "required",
    "expected_file_path",
    "status",
]

# 값이 None일 수 있어 키 존재만 검사하는 필드
ITEM_NULLABLE_FIELDS = ["actual_file_path", "notes"]

MANIFEST_DISCLAIMER = (
    "Asset intake manifest. Files are registered as metadata only — "
    "no copy, no upload, no external calls."
)

# asset_type → (워크스페이스 하위 폴더, source_stage, provider_hint, 기본 확장자)
_TYPE_INFO = {
    "image": ("images", "VISUAL", "midjourney", ".png"),
    "motion": ("motion", "MOTION", "midjourney_video", ".mp4"),
    "audio": ("audio", "VOICE", "typecast", ".wav"),
    "subtitle": ("subtitles", "SUBTITLE", "manual", ".srt"),
    "video": ("video", "EDITING", "manual", ".mp4"),
    "thumbnail": ("thumbnail", "EDITING", "manual", ".png"),
}

# 참고한 입력 파일 후보 (존재하는 것만 sources에 기록)
_SOURCE_CANDIDATES = [
    "assets/asset_requirements.json",
    "assets/images/visual_plan.json",
    "assets/motion/motion_plan.json",
    "assets/audio/voice_plan.json",
    "assets/subtitles/subtitle_plan.json",
    "edit/editing_plan.json",
    "providers/exports/midjourney_prompt_pack.json",
    "providers/exports/midjourney_video_prompt_pack.json",
    "providers/exports/typecast_script_pack.json",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ManualIntakeManager:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger
        self.workspaces = ManualWorkspaceManager(logger)

    def manifest_path(self, project_path: str | Path) -> Path:
        return self.workspaces.workspace_path(project_path) / MANIFEST_FILE

    def _expected_names(self, project_path: Path, asset_type: str, count: int) -> list:
        """plan이 있으면 plan 기반, 없으면 generic한 기대 파일명을 만든다."""
        if asset_type == "image":
            plan_path = project_path / "assets" / "images" / "visual_plan.json"
            if plan_path.is_file():
                names = []
                for sv in load_json(plan_path)["scene_visuals"]:
                    for n in range(sv["required_image_count"]):
                        names.append(f"{sv['scene_id']}_v{n + 1}.png")
                return names
        elif asset_type == "motion":
            plan_path = project_path / "assets" / "motion" / "motion_plan.json"
            if plan_path.is_file():
                return [
                    f"{sm['scene_id']}_motion.mp4"
                    for sm in load_json(plan_path)["scene_motions"]
                ]
        elif asset_type == "audio":
            plan_path = project_path / "assets" / "audio" / "voice_plan.json"
            if plan_path.is_file():
                return [
                    f"{nb['block_id']}.wav"
                    for nb in load_json(plan_path)["narration_blocks"]
                ]
        elif asset_type == "subtitle":
            plan_path = project_path / "assets" / "subtitles" / "subtitle_plan.json"
            if plan_path.is_file():
                return [
                    f"subtitles_{lang}.srt"
                    for lang in load_json(plan_path)["target_languages"]
                ]
        elif asset_type == "video":
            return ["final_video.mp4"] if count == 1 else [
                f"final_video_{n + 1}.mp4" for n in range(count)
            ]
        elif asset_type == "thumbnail":
            return ["thumbnail.png"] if count == 1 else [
                f"thumbnail_{n + 1}.png" for n in range(count)
            ]
        ext = _TYPE_INFO[asset_type][3]
        return [f"{asset_type}_{n + 1:03d}{ext}" for n in range(count)]

    def create_asset_intake_manifest(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        workspace = self.workspaces.workspace_path(project_path)

        # 기대 수량: asset_requirements가 있으면 그것을, 없으면 최소 기본값
        requirements_path = project_path / "assets" / "asset_requirements.json"
        if requirements_path.is_file():
            expected_counts = load_json(requirements_path)["expected_counts"]
        else:
            expected_counts = {"video": 1, "thumbnail": 1}

        # 워크스페이스 폴더명 기준의 루트 상대 경로 (예: manual_assets/{pid})
        workspace_rel = Path(workspace.parent.name) / workspace.name

        items = []
        for asset_type in SUPPORTED_ASSET_TYPES:
            count = expected_counts.get(asset_type, 0)
            if count <= 0:
                continue
            folder, source_stage, provider_hint, _ = _TYPE_INFO[asset_type]
            for name in self._expected_names(project_path, asset_type, count):
                items.append({
                    "item_id": f"MI{len(items) + 1:03d}",
                    "asset_type": asset_type,
                    "source_stage": source_stage,
                    "provider_hint": provider_hint,
                    "required": True,
                    "expected_file_path": (workspace_rel / folder / name).as_posix(),
                    "actual_file_path": None,
                    "status": STATUS_WAITING,
                    "notes": None,
                })

        manifest = {
            "project_id": project["project_id"],
            "intake_mode": "manual",
            "workspace_path": str(workspace),
            "sources": [
                rel for rel in _SOURCE_CANDIDATES if (project_path / rel).is_file()
            ],
            "items": items,
            "created_at": _now_iso(),
            "disclaimer": MANIFEST_DISCLAIMER,
        }
        write_json(self.manifest_path(project_path), manifest)
        if self.logger:
            self.logger.info(
                f"asset intake manifest 생성: {len(items)} items",
                metadata={"project_id": project["project_id"], "items": len(items)},
            )
        return manifest

    def load_asset_intake_manifest(self, project_path: str | Path) -> dict:
        path = self.manifest_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"asset_intake_manifest.json이 없습니다: {path}",
                location="ManualIntakeManager.load_asset_intake_manifest",
                suggested_fix="create_asset_intake_manifest를 먼저 실행하세요.",
            )
        return load_json(path)

    def update_asset_intake_item(
        self,
        project_path: str | Path,
        item_id: str,
        file_path: str | None = None,
        notes: str | None = None,
    ) -> dict:
        manifest = self.load_asset_intake_manifest(project_path)
        for item in manifest["items"]:
            if item["item_id"] == item_id:
                if file_path is not None:
                    item["actual_file_path"] = str(file_path)
                    if item["status"] == STATUS_WAITING:
                        item["status"] = STATUS_ASSIGNED
                if notes is not None:
                    item["notes"] = notes
                write_json(self.manifest_path(project_path), manifest)
                if self.logger:
                    self.logger.info(
                        f"intake item 갱신: {item_id} ({item['status']})",
                        metadata={"item_id": item_id, "status": item["status"]},
                    )
                return item
        raise ADOSFileNotFoundError(
            f"intake item을 찾을 수 없습니다: {item_id}",
            location="ManualIntakeManager.update_asset_intake_item",
            suggested_fix="asset_intake_manifest.json의 item_id를 확인하세요.",
        )

    def validate_asset_intake_manifest(self, project_path: str | Path) -> bool:
        manifest = self.load_asset_intake_manifest(project_path)
        loc = "ManualIntakeManager.validate_asset_intake_manifest"
        ADOSValidator.require_fields(
            manifest, ["project_id", "intake_mode", "workspace_path", "items"],
            location=loc,
        )
        for item in manifest["items"]:
            ADOSValidator.require_fields(item, ITEM_REQUIRED_FIELDS, location=loc)
            missing = [f for f in ITEM_NULLABLE_FIELDS if f not in item]
            if missing:
                raise ADOSValidationError(
                    f"필수 필드 누락: {', '.join(missing)}", location=loc,
                    suggested_fix=f"다음 필드를 추가하세요: {', '.join(missing)}",
                )
            ADOSValidator.validate_enum(
                item["asset_type"], SUPPORTED_ASSET_TYPES,
                field="asset_type", location=loc,
            )
        return True
