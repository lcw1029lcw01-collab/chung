# -*- coding: utf-8 -*-
"""Provider job manager (v0.2 — manual integration preparation).

수동 Provider 작업(job)의 생성·추적을 관리한다.
외부 호출은 없다. external_call_made는 v0.2에서 항상 false다.
근거: docs/32_PROVIDER_INTEGRATION_V0_2.md
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

PROVIDERS_DIR = "providers"
QUEUE_FILE = "job_queue.json"
JOBS_SUBDIR = "provider_jobs"

SUPPORTED_PROVIDERS = ["midjourney", "midjourney_video", "typecast"]

SUPPORTED_STATUSES = [
    "CREATED",
    "EXPORTED",
    "WAITING_MANUAL_WORK",
    "ASSET_IMPORTED",
    "REVIEW_REQUIRED",
    "COMPLETED",
    "CANCELLED",
]

JOB_REQUIRED_FIELDS = [
    "job_id",
    "provider_name",
    "job_type",
    "source_ref",
    "payload",
    "status",
    "external_call_made",
    "created_at",
    "updated_at",
    "notes",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProviderJobManager:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def queue_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PROVIDERS_DIR / QUEUE_FILE

    def job_path(self, project_path: str | Path, job_id: str) -> Path:
        return Path(project_path) / PROVIDERS_DIR / JOBS_SUBDIR / f"{job_id}.json"

    def create_job_queue(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        queue = {
            "project_id": project["project_id"],
            "queue_mode": "manual",
            "external_call_made": False,
            "jobs": [],
            "created_at": _now_iso(),
        }
        write_json(self.queue_path(project_path), queue)
        return queue

    def load_job_queue(self, project_path: str | Path) -> dict:
        path = self.queue_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"job_queue.json이 없습니다: {path}",
                location="ProviderJobManager.load_job_queue",
                suggested_fix="create_job_queue를 먼저 실행하세요.",
            )
        return load_json(path)

    def create_provider_job(
        self,
        project_path: str | Path,
        provider_name: str,
        job_type: str,
        source_ref: str,
        payload: dict,
    ) -> dict:
        project_path = Path(project_path)
        ADOSValidator.validate_enum(
            provider_name, SUPPORTED_PROVIDERS, field="provider_name",
            location="ProviderJobManager.create_provider_job",
        )
        queue = self.load_job_queue(project_path)
        now = _now_iso()
        job = {
            "job_id": f"PJ{len(queue['jobs']) + 1:03d}-{provider_name}",
            "provider_name": provider_name,
            "job_type": job_type,
            "source_ref": source_ref,
            "payload": payload,
            "status": "CREATED",
            "external_call_made": False,  # v0.2에서는 항상 false
            "created_at": now,
            "updated_at": now,
            "notes": None,
        }
        queue["jobs"].append(job)
        write_json(self.queue_path(project_path), queue)
        write_json(self.job_path(project_path, job["job_id"]), job)
        if self.logger:
            self.logger.info(
                f"provider job 생성: {job['job_id']}",
                metadata={"job_id": job["job_id"], "provider": provider_name},
            )
        return job

    def update_job_status(
        self, project_path: str | Path, job_id: str,
        status: str, notes: str | None = None,
    ) -> dict:
        project_path = Path(project_path)
        ADOSValidator.validate_enum(
            status, SUPPORTED_STATUSES, field="status",
            location="ProviderJobManager.update_job_status",
        )
        queue = self.load_job_queue(project_path)
        for job in queue["jobs"]:
            if job["job_id"] == job_id:
                job["status"] = status
                job["updated_at"] = _now_iso()
                if notes is not None:
                    job["notes"] = notes
                write_json(self.queue_path(project_path), queue)
                write_json(self.job_path(project_path, job_id), job)
                if self.logger:
                    self.logger.info(
                        f"provider job 상태 변경: {job_id} → {status}",
                        metadata={"job_id": job_id, "status": status},
                    )
                return job
        raise ADOSFileNotFoundError(
            f"job을 찾을 수 없습니다: {job_id}",
            location="ProviderJobManager.update_job_status",
            suggested_fix="job_queue.json의 job_id를 확인하세요.",
        )

    def validate_job_queue(self, project_path: str | Path) -> bool:
        queue = self.load_job_queue(project_path)
        loc = "ProviderJobManager.validate_job_queue"
        ADOSValidator.require_fields(
            queue, ["project_id", "queue_mode", "jobs"], location=loc
        )
        for job in queue["jobs"]:
            ADOSValidator.require_fields(
                job, [f for f in JOB_REQUIRED_FIELDS if f != "notes"], location=loc
            )
            ADOSValidator.validate_enum(
                job["provider_name"], SUPPORTED_PROVIDERS,
                field="provider_name", location=loc,
            )
            ADOSValidator.validate_enum(
                job["status"], SUPPORTED_STATUSES, field="status", location=loc
            )
            ADOSValidator.validate_enum(
                job["external_call_made"], [False],
                field="external_call_made", location=loc,
            )
        return True
