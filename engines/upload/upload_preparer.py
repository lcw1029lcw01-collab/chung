# -*- coding: utf-8 -*-
"""Upload preparer (upload-preparation skeleton).

YouTube 업로드를 위한 메타데이터 패키지·체크리스트·수동 업로드 안내를 만든다.

주의: 업로드하지 않는다. OAuth/API 로직이 없다.
final_upload_gate.upload_ready가 true가 아니면 upload_ready를 true로 만들지 않는다.
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

PACKAGE_DIR = "package"
METADATA_FILE = "youtube_metadata_package.json"
CHECKLIST_FILE = "upload_readiness_checklist.json"
INSTRUCTIONS_FILE = "manual_upload_instructions.json"

REQUIRED_INPUTS = [
    ("package/publishing_plan.json", "PublishingEngine.create_dummy_package"),
    ("story/script_draft.json", "StoryEngine.create_dummy_story"),
    ("reports/final_upload_gate.json", "FinalQualityGate.create_final_quality_report"),
]

METADATA_REQUIRED_FIELDS = [
    "project_id",
    "platform",
    "upload_mode",
    "title",
    "description",
    "tags",
    "target_languages",
    "default_language",
    "upload_ready",
    "blocked_by_final_gate",
    "created_at",
    "disclaimer",
]

METADATA_DISCLAIMER = "YouTube metadata package only. No upload was performed."
INSTRUCTIONS_WARNING = "Manual upload only. This system did not upload any video."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class UploadPreparer:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def metadata_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PACKAGE_DIR / METADATA_FILE

    def checklist_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PACKAGE_DIR / CHECKLIST_FILE

    def instructions_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PACKAGE_DIR / INSTRUCTIONS_FILE

    def _load_gate(self, project_path: Path) -> dict:
        return load_json(project_path / "reports" / "final_upload_gate.json")

    def create_youtube_metadata_package(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for rel, fix in REQUIRED_INPUTS:
            if not (project_path / rel).is_file():
                raise ADOSFileNotFoundError(
                    f"{rel}가 없습니다: {project_path / rel}",
                    location="UploadPreparer.create_youtube_metadata_package",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        project = load_json(project_path / "project.json")
        plan = load_json(project_path / "package" / "publishing_plan.json")
        gate = self._load_gate(project_path)

        # upload_ready는 final gate가 단일 기준 — 절대 강제로 true로 만들지 않는다
        upload_ready = bool(gate["upload_ready"])
        package = {
            "project_id": project["project_id"],
            "platform": "youtube",
            "upload_mode": "manual_preparation",
            "title": plan["title"],
            "description": plan["description"],
            "tags": plan["tags"],
            "target_languages": plan["target_languages"],
            "default_language": project["languages"]["master_language"],
            "upload_ready": upload_ready,
            "blocked_by_final_gate": not upload_ready,
            "created_at": _now_iso(),
            "disclaimer": METADATA_DISCLAIMER,
        }
        write_json(self.metadata_path(project_path), package)
        return package

    def create_upload_readiness_checklist(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        gate_path = project_path / "reports" / "final_upload_gate.json"
        if not gate_path.is_file():
            raise ADOSFileNotFoundError(
                f"final_upload_gate.json이 없습니다: {gate_path}",
                location="UploadPreparer.create_upload_readiness_checklist",
                suggested_fix="FinalQualityGate.create_final_quality_report를 먼저 실행하세요.",
            )
        project = load_json(project_path / "project.json")
        gate = self._load_gate(project_path)

        def _asset_present(asset_type: str) -> bool:
            manifest_path = project_path / "assets" / "production_asset_manifest.json"
            if not manifest_path.is_file():
                return False
            manifest = load_json(manifest_path)
            return any(
                a["asset_type"] == asset_type and a["exists"] for a in manifest["assets"]
            )

        review_approved = False
        summary_path = project_path / "reports" / "human_review_summary.json"
        if summary_path.is_file():
            review_approved = load_json(summary_path)["all_required_approved"]

        checklist = {
            "project_id": project["project_id"],
            "final_video_present": _asset_present("video"),
            "thumbnail_present": _asset_present("thumbnail"),
            "subtitles_present": _asset_present("subtitle"),
            "metadata_present": self.metadata_path(project_path).is_file(),
            "human_review_approved": review_approved,
            "final_quality_passed": gate["gate_result"] == "PASS",
            "upload_ready": bool(gate["upload_ready"]),
            "blockers": gate["blockers"],
            "created_at": _now_iso(),
        }
        write_json(self.checklist_path(project_path), checklist)
        return checklist

    def create_manual_upload_instructions(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        instructions = {
            "project_id": project["project_id"],
            "platform": "youtube",
            "steps": [
                "1. assets/production_asset_manifest.json의 최종 영상 파일을 확인한다.",
                "2. 썸네일 파일을 확인한다.",
                "3. package/youtube_metadata_package.json의 제목/설명/태그를 YouTube Studio에 복사한다.",
                "4. 언어별 자막 파일을 업로드한다.",
                "5. 공개 범위/예약 시간을 설정한다.",
                "6. 업로드 후 package/published_record.json을 실제 URL로 갱신한다.",
            ],
            "warning": INSTRUCTIONS_WARNING,
            "created_at": _now_iso(),
        }
        write_json(self.instructions_path(project_path), instructions)
        return instructions

    def validate_upload_package(self, project_path: str | Path) -> bool:
        project_path = Path(project_path)
        loc = "UploadPreparer.validate_upload_package"
        for path in (
            self.metadata_path(project_path),
            self.checklist_path(project_path),
            self.instructions_path(project_path),
        ):
            if not path.is_file():
                raise ADOSFileNotFoundError(
                    f"업로드 패키지 파일이 없습니다: {path}",
                    location=loc,
                    suggested_fix="UploadPreparer의 create_* 메서드를 먼저 실행하세요.",
                )
        package = load_json(self.metadata_path(project_path))
        ADOSValidator.require_fields(package, METADATA_REQUIRED_FIELDS, location=loc)
        return True
