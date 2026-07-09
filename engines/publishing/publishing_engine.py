# -*- coding: utf-8 -*-
"""Publishing engine (walking skeleton).

품질 게이트 통과 후 더미 업로드 패키지·준비 상태·게시 기록을 만든다.
전체 스키마는 docs/28_PUBLISHING_ENGINE.md 기준으로 이후 확장한다.

주의: 아무것도 업로드하지 않는다. mp4를 만들지 않는다.
게시는 SIMULATED_NOT_UPLOADED로만 기록한다.
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

PACKAGE_DIR = "package"
MANIFEST_FILE = "package_manifest.json"

REQUIRED_INPUTS = [
    ("reports/quality_gate.json", "QualityEngine.create_dummy_quality_report"),
    ("edit/editing_plan.json", "EditingEngine.create_dummy_editing_plan"),
    ("story/script_draft.json", "StoryEngine.create_dummy_story"),
    ("assets/images/visual_plan.json", "VisualEngine.create_dummy_visual_plan"),
    ("assets/audio/voice_plan.json", "VoiceEngine.create_dummy_voice_plan"),
    ("assets/subtitles/subtitle_plan.json", "SubtitleEngine.create_dummy_subtitle_plan"),
]

MANIFEST_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "package_mode",
    "production_ready",
    "final_video_file",
    "thumbnail_file",
    "subtitle_files",
    "metadata_files",
    "required_assets",
    "missing_real_assets",
    "created_at",
    "disclaimer",
]

PLAN_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "publishing_mode",
    "platform_hint",
    "title",
    "description",
    "tags",
    "target_languages",
    "upload_ready",
    "reason_not_upload_ready",
    "created_at",
]

DUMMY_DISCLAIMER = "Dummy package manifest. No real uploadable video generated."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class PublishingEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def manifest_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PACKAGE_DIR / MANIFEST_FILE

    def ready_state_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PACKAGE_DIR / "ready_state.json"

    def published_record_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PACKAGE_DIR / "published_record.json"

    def create_dummy_package(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        for rel, fix in REQUIRED_INPUTS:
            if not (project_path / rel).is_file():
                raise ADOSFileNotFoundError(
                    f"{rel}가 없습니다: {project_path / rel}",
                    location="PublishingEngine.create_dummy_package",
                    suggested_fix=f"{fix}를 먼저 실행하세요.",
                )
        gate = load_json(project_path / "reports" / "quality_gate.json")
        if gate["gate_result"] != "PASS":
            raise ADOSValidationError(
                f"품질 게이트가 PASS가 아닙니다: {gate['gate_result']}",
                location="PublishingEngine.create_dummy_package",
                suggested_fix="Quality 단계를 통과한 뒤 패키징하세요.",
            )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        script = load_json(project_path / "story" / "script_draft.json")

        title = topic["title"]
        manifest = {
            "project_id": project["project_id"],
            "topic": title,
            "package_mode": "dummy",
            "production_ready": False,
            "final_video_file": None,
            "thumbnail_file": None,
            "subtitle_files": [],
            "metadata_files": [
                "package/publishing_plan.json",
                "package/upload_package.json",
            ],
            "required_assets": [rel for rel, _ in REQUIRED_INPUTS],
            "missing_real_assets": [
                "final_video_file",
                "thumbnail_file",
                "voice_audio_files",
                "subtitle_files",
            ],
            "created_at": _now_iso(),
            "disclaimer": DUMMY_DISCLAIMER,
        }
        folder = project_path / PACKAGE_DIR
        write_json(folder / MANIFEST_FILE, manifest)
        write_json(
            folder / "upload_package.json",
            {
                "project_id": project["project_id"],
                "package_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "contents": manifest["metadata_files"],
                "upload_ready": False,
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "publishing_plan.json",
            {
                "project_id": project["project_id"],
                "topic": title,
                "publishing_mode": "dummy",
                "platform_hint": "youtube",
                "title": script["title"],
                "description": f"'{title}'에 대한 영상 설명 (placeholder).",
                "tags": ["placeholder", topic["category"]],
                "target_languages": project["languages"]["target_languages"],
                "upload_ready": False,
                "reason_not_upload_ready": (
                    "더미 파이프라인 — 실제 영상/썸네일/오디오/자막 파일이 생성되지 않았다."
                ),
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 패키지 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return manifest

    def create_dummy_ready_state(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        if not self.manifest_path(project_path).is_file():
            raise ADOSFileNotFoundError(
                f"package_manifest.json이 없습니다: {self.manifest_path(project_path)}",
                location="PublishingEngine.create_dummy_ready_state",
                suggested_fix="create_dummy_package를 먼저 실행하세요.",
            )
        manifest = load_json(self.manifest_path(project_path))
        ready_state = {
            "project_id": manifest["project_id"],
            "status": "DUMMY_READY_ONLY",
            "upload_ready": False,
            "real_upload_blocked": True,
            "created_at": _now_iso(),
        }
        write_json(self.ready_state_path(project_path), ready_state)
        return ready_state

    def create_dummy_published_record(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        if not self.ready_state_path(project_path).is_file():
            raise ADOSFileNotFoundError(
                f"ready_state.json이 없습니다: {self.ready_state_path(project_path)}",
                location="PublishingEngine.create_dummy_published_record",
                suggested_fix="create_dummy_ready_state를 먼저 실행하세요.",
            )
        ready = load_json(self.ready_state_path(project_path))
        record = {
            "project_id": ready["project_id"],
            "publication_status": "SIMULATED_NOT_UPLOADED",
            "platform": "youtube",
            "video_url": None,
            "uploaded_at": None,
            "created_at": _now_iso(),
        }
        write_json(self.published_record_path(project_path), record)
        return record

    def load_package_manifest(self, project_path: str | Path) -> dict:
        path = self.manifest_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"package_manifest.json이 없습니다: {path}",
                location="PublishingEngine.load_package_manifest",
                suggested_fix="create_dummy_package를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_publishing_package(self, project_path: str | Path) -> bool:
        loc = "PublishingEngine.validate_publishing_package"
        manifest = self.load_package_manifest(project_path)
        ADOSValidator.require_fields(
            manifest,
            [f for f in MANIFEST_REQUIRED_FIELDS
             if f not in ("final_video_file", "thumbnail_file")],  # null 허용 필드 제외
            location=loc,
        )
        plan = load_json(Path(project_path) / PACKAGE_DIR / "publishing_plan.json")
        ADOSValidator.require_fields(plan, PLAN_REQUIRED_FIELDS, location=loc)
        return True
