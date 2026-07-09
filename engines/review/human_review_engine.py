# -*- coding: utf-8 -*-
"""Human review engine (upload-preparation skeleton).

사람 검토 체크포인트를 관리한다. 사람 검토는 게이트다 —
필수 체크포인트가 전부 승인되기 전에는 업로드 허용이 false를 유지한다.
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

REPORTS_DIR = "reports"
CHECKPOINTS_FILE = "human_review_checkpoints.json"
SUMMARY_FILE = "human_review_summary.json"

DEFAULT_CHECKPOINTS = [
    ("STORY_REVIEW", "STORY"),
    ("DIRECTION_REVIEW", "DIRECTION"),
    ("VISUAL_REVIEW", "VISUAL"),
    ("EDITING_REVIEW", "EDITING"),
    ("QUALITY_REVIEW", "QUALITY"),
    ("UPLOAD_REVIEW", "UPLOAD"),
]

SUMMARY_REQUIRED_FIELDS = [
    "project_id",
    "total_checkpoints",
    "approved_count",
    "rejected_count",
    "pending_count",
    "all_required_approved",
    "upload_allowed_by_human_review",
    "created_at",
    "updated_at",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class HumanReviewEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def checkpoints_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / CHECKPOINTS_FILE

    def summary_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / REPORTS_DIR / SUMMARY_FILE

    def create_review_checkpoints(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        data = {
            "project_id": project["project_id"],
            "checkpoints": [
                {
                    "checkpoint_id": checkpoint_id,
                    "stage": stage,
                    "status": "PENDING",
                    "reviewer": None,
                    "notes": None,
                    "updated_at": None,
                }
                for checkpoint_id, stage in DEFAULT_CHECKPOINTS
            ],
            "created_at": _now_iso(),
        }
        write_json(self.checkpoints_path(project_path), data)
        self._write_summary(project_path, data, created_at=data["created_at"])
        return data

    def _load_checkpoints(self, project_path: Path) -> dict:
        path = self.checkpoints_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"human_review_checkpoints.json이 없습니다: {path}",
                location="HumanReviewEngine._load_checkpoints",
                suggested_fix="create_review_checkpoints를 먼저 실행하세요.",
            )
        return load_json(path)

    def _set_status(
        self, project_path: str | Path, checkpoint_id: str,
        status: str, reviewer: str, notes: str | None,
    ) -> dict:
        project_path = Path(project_path)
        data = self._load_checkpoints(project_path)
        for checkpoint in data["checkpoints"]:
            if checkpoint["checkpoint_id"] == checkpoint_id:
                checkpoint["status"] = status
                checkpoint["reviewer"] = reviewer
                checkpoint["notes"] = notes
                checkpoint["updated_at"] = _now_iso()
                break
        else:
            raise ADOSValidationError(
                f"알 수 없는 checkpoint_id: {checkpoint_id}",
                location="HumanReviewEngine._set_status",
                suggested_fix=f"사용 가능한 체크포인트: {', '.join(c for c, _ in DEFAULT_CHECKPOINTS)}",
            )
        write_json(self.checkpoints_path(project_path), data)
        created_at = load_json(self.summary_path(project_path))["created_at"] \
            if self.summary_path(project_path).is_file() else _now_iso()
        summary = self._write_summary(project_path, data, created_at=created_at)
        if self.logger:
            self.logger.info(
                f"리뷰 체크포인트 {status}: {checkpoint_id}",
                metadata={"checkpoint_id": checkpoint_id, "status": status},
            )
        return summary

    def approve_checkpoint(
        self, project_path: str | Path, checkpoint_id: str,
        reviewer: str = "human", notes: str | None = None,
    ) -> dict:
        return self._set_status(project_path, checkpoint_id, "APPROVED", reviewer, notes)

    def reject_checkpoint(
        self, project_path: str | Path, checkpoint_id: str,
        reviewer: str = "human", notes: str | None = None,
    ) -> dict:
        return self._set_status(project_path, checkpoint_id, "REJECTED", reviewer, notes)

    def _write_summary(self, project_path: Path, data: dict, created_at: str) -> dict:
        statuses = [c["status"] for c in data["checkpoints"]]
        approved = statuses.count("APPROVED")
        rejected = statuses.count("REJECTED")
        pending = statuses.count("PENDING")
        all_approved = approved == len(statuses) and len(statuses) > 0
        summary = {
            "project_id": data["project_id"],
            "total_checkpoints": len(statuses),
            "approved_count": approved,
            "rejected_count": rejected,
            "pending_count": pending,
            "all_required_approved": all_approved,
            "upload_allowed_by_human_review": all_approved,
            "created_at": created_at,
            "updated_at": _now_iso(),
        }
        write_json(self.summary_path(project_path), summary)
        return summary

    def load_review_summary(self, project_path: str | Path) -> dict:
        path = self.summary_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"human_review_summary.json이 없습니다: {path}",
                location="HumanReviewEngine.load_review_summary",
                suggested_fix="create_review_checkpoints를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_review_summary(self, project_path: str | Path) -> bool:
        summary = self.load_review_summary(project_path)
        ADOSValidator.require_fields(
            summary, SUMMARY_REQUIRED_FIELDS,
            location="HumanReviewEngine.validate_review_summary",
        )
        return True
