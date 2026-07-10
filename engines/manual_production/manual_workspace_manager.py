# -*- coding: utf-8 -*-
"""Manual workspace manager (v0.2 — manual production loop).

사람이 외부 도구로 생성한 자산을 배치할 gitignore된 워크스페이스를
manual_assets/{project_id}/ 아래에 만든다. 파일 복사·업로드는 하지 않는다.
근거: docs/33_MANUAL_PRODUCTION_LOOP_V0_2.md #5
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSPathManager,
    ADOSValidator,
    ensure_directory,
    load_json,
    load_yaml,
    write_json,
    write_text,
)

INFO_FILE = "workspace_info.json"
README_FILE = "README.md"

DEFAULT_WORKSPACE_ROOT = "manual_assets"

ASSET_FOLDERS = [
    "images",
    "motion",
    "audio",
    "subtitles",
    "video",
    "thumbnail",
    "notes",
]

INFO_REQUIRED_FIELDS = [
    "project_id",
    "project_path",
    "workspace_path",
    "asset_folders",
    "allow_file_copy",
    "upload_ready",
    "created_at",
    "disclaimer",
]

WORKSPACE_DISCLAIMER = (
    "Manual workspace only. Files placed here are not automatically uploaded."
)

README_TEXT = """# Manual Asset Workspace

이 폴더는 사람이 외부 도구(Midjourney/Typecast 등)로 생성한 파일을
배치하는 곳이다. **자동 업로드되지 않으며, git에 커밋되지 않는다.**

1. asset_intake_manifest.json의 item별 expected_file_path를 확인한다.
2. 생성한 파일을 해당 하위 폴더(images/, motion/, audio/, subtitles/,
   video/, thumbnail/)에 둔다.
3. ManualIntakeManager.update_asset_intake_item()으로 actual_file_path를 기록한다.
4. ManualProductionLoop.import_ready_assets()로 메타데이터만 등록한다 (복사 없음).
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_workspace_root(project_path: str | Path) -> Path:
    """project_path에서 ADOS 루트를 찾아 manual_assets 루트를 돌려준다.

    config/manual_production.yaml의 manual_workspace_root를 따르고,
    없으면 기본값 manual_assets를 쓴다.
    """
    root = ADOSPathManager.find_project_root(Path(project_path))
    config_path = root / "config" / "manual_production.yaml"
    workspace_root = DEFAULT_WORKSPACE_ROOT
    if config_path.is_file():
        config = load_yaml(config_path)
        if isinstance(config, dict) and config.get("manual_workspace_root"):
            workspace_root = config["manual_workspace_root"]
    return root / workspace_root


class ManualWorkspaceManager:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def workspace_path(self, project_path: str | Path) -> Path:
        project = load_json(Path(project_path) / "project.json")
        return resolve_workspace_root(project_path) / project["project_id"]

    def info_path(self, project_path: str | Path) -> Path:
        return self.workspace_path(project_path) / INFO_FILE

    def create_manual_workspace(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        workspace = self.workspace_path(project_path)

        for folder in ASSET_FOLDERS:
            ensure_directory(workspace / folder)

        info = {
            "project_id": project["project_id"],
            "project_path": str(project_path),
            "workspace_path": str(workspace),
            "asset_folders": list(ASSET_FOLDERS),
            "allow_file_copy": False,
            "upload_ready": False,
            "created_at": _now_iso(),
            "disclaimer": WORKSPACE_DISCLAIMER,
        }
        write_json(workspace / INFO_FILE, info)
        write_text(workspace / README_FILE, README_TEXT)
        if self.logger:
            self.logger.info(
                f"수동 워크스페이스 생성: {workspace}",
                metadata={"project_id": project["project_id"]},
            )
        return info

    def load_workspace_info(self, project_path: str | Path) -> dict:
        path = self.info_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"workspace_info.json이 없습니다: {path}",
                location="ManualWorkspaceManager.load_workspace_info",
                suggested_fix="create_manual_workspace를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_manual_workspace(self, project_path: str | Path) -> bool:
        info = self.load_workspace_info(project_path)
        loc = "ManualWorkspaceManager.validate_manual_workspace"
        ADOSValidator.require_fields(info, INFO_REQUIRED_FIELDS, location=loc)
        workspace = Path(info["workspace_path"])
        for folder in ASSET_FOLDERS:
            if not (workspace / folder).is_dir():
                raise ADOSFileNotFoundError(
                    f"워크스페이스 하위 폴더가 없습니다: {workspace / folder}",
                    location=loc,
                    suggested_fix="create_manual_workspace를 다시 실행하세요.",
                )
        return True
