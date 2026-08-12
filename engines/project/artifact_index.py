# -*- coding: utf-8 -*-
"""Artifact index — 프로젝트의 중요한 산출물을 등록·조회한다.

규칙:
- 절대 경로를 저장하지 않는다 (프로젝트 루트 기준 상대 경로만).
- 프로젝트 루트 밖으로 탈출하는 경로를 금지한다.
- 실제 파일을 복사하지 않는다 (메타데이터와 checksum만 기록).
"""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from core import ADOSFileNotFoundError, ADOSValidationError, load_json, write_json

INDEX_REL = Path("runtime") / "artifact_index.json"

ARTIFACT_STATUSES = ["READY", "EXPECTED", "REJECTED", "SUPERSEDED"]

# checksum 청크 크기 — 대용량 영상도 메모리 부담 없이 해시
_CHUNK = 1024 * 1024


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


class ArtifactIndex:
    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path).resolve()
        self.index_path = self.project_path / INDEX_REL

    def _load(self) -> dict:
        if not self.index_path.is_file():
            return {"artifacts": {}, "updated_at": None}
        return load_json(self.index_path)

    def _save(self, data: dict) -> None:
        data["updated_at"] = _now_iso()
        write_json(self.index_path, data)

    def _validate_relative(self, relative_path: str) -> Path:
        rel = Path(str(relative_path))
        if rel.is_absolute() or str(relative_path).startswith(("\\", "/")):
            raise ADOSValidationError(
                f"artifact 경로는 상대 경로여야 합니다: {relative_path}",
                location="ArtifactIndex._validate_relative",
                suggested_fix="프로젝트 루트 기준 상대 경로를 사용하세요.",
            )
        resolved = (self.project_path / rel).resolve()
        if resolved != self.project_path and self.project_path not in resolved.parents:
            raise ADOSValidationError(
                f"artifact 경로가 프로젝트 루트를 벗어납니다: {relative_path}",
                location="ArtifactIndex._validate_relative",
                suggested_fix="'..' 등 루트 탈출 요소를 제거하세요.",
            )
        return resolved

    def register(
        self,
        artifact_key: str,
        relative_path: str,
        producer_stage: str,
        media_type: str = "application/json",
        status: str = "READY",
        metadata: dict | None = None,
        require_exists: bool = True,
    ) -> dict:
        if status not in ARTIFACT_STATUSES:
            raise ADOSValidationError(
                f"허용되지 않는 artifact status: {status}",
                location="ArtifactIndex.register",
            )
        resolved = self._validate_relative(relative_path)
        checksum = None
        if resolved.is_file():
            checksum = file_checksum(resolved)
        elif require_exists and status == "READY":
            raise ADOSFileNotFoundError(
                f"artifact 파일이 없습니다: {relative_path}",
                location="ArtifactIndex.register",
                suggested_fix="파일을 먼저 생성한 뒤 등록하세요.",
            )

        data = self._load()
        previous = data["artifacts"].get(artifact_key)
        entry = {
            "artifact_key": artifact_key,
            "relative_path": str(relative_path).replace("\\", "/"),
            "producer_stage": producer_stage,
            "media_type": media_type,
            "version": (previous["version"] + 1) if previous else 1,
            "checksum": checksum,
            "status": status,
            "created_at": _now_iso(),
            "metadata": metadata or {},
        }
        data["artifacts"][artifact_key] = entry
        self._save(data)
        return entry

    def get(self, artifact_key: str) -> dict | None:
        return self._load()["artifacts"].get(artifact_key)

    def all(self) -> dict:
        return self._load()["artifacts"]

    def exists(self, artifact_key: str) -> bool:
        """등록되어 있고 실제 파일도 존재해야 true."""
        entry = self.get(artifact_key)
        if not entry or entry["status"] != "READY":
            return False
        return (self.project_path / entry["relative_path"]).is_file()

    def resolve_path(self, artifact_key: str) -> Path:
        entry = self.get(artifact_key)
        if not entry:
            raise ADOSFileNotFoundError(
                f"등록되지 않은 artifact: {artifact_key}",
                location="ArtifactIndex.resolve_path",
                suggested_fix="해당 단계를 먼저 실행해 artifact를 생성하세요.",
            )
        return self.project_path / entry["relative_path"]

    def load_json_artifact(self, artifact_key: str) -> dict:
        return load_json(self.resolve_path(artifact_key))
