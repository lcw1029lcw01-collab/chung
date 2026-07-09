# -*- coding: utf-8 -*-
"""ADOS structured errors.

에러 필수 정보(docs/02_DEVELOPMENT_RULES.md #12):
error_type, message, location, project_id, stage, cause, suggested_fix, created_at
"""
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ADOSError(Exception):
    """모든 ADOS 에러의 베이스. 에러는 조용히 무시하지 않는다."""

    def __init__(
        self,
        message: str,
        location: str = "",
        project_id: str = "",
        stage: str = "",
        cause: str = "",
        suggested_fix: str = "",
    ):
        super().__init__(message)
        self.message = message
        self.location = location
        self.project_id = project_id
        self.stage = stage
        self.cause = cause
        self.suggested_fix = suggested_fix
        self.created_at = _now_iso()

    def to_dict(self) -> dict:
        return {
            "error_type": type(self).__name__,
            "message": self.message,
            "location": self.location,
            "project_id": self.project_id,
            "stage": self.stage,
            "cause": self.cause,
            "suggested_fix": self.suggested_fix,
            "created_at": self.created_at,
        }


class ADOSValidationError(ADOSError):
    """필수 필드/값 검증 실패."""


class ADOSFileNotFoundError(ADOSError):
    """필수 파일 또는 폴더 없음."""


class ADOSConfigError(ADOSError):
    """config 로딩/키 누락 오류."""


class ADOSEngineError(ADOSError):
    """엔진 실행 중 오류."""


class ADOSErrorReporter:
    """에러를 구조화된 dict로 만들고, logger가 있으면 기록한다."""

    def __init__(self, logger=None):
        self._logger = logger

    def report(self, error: Exception) -> dict:
        if isinstance(error, ADOSError):
            data = error.to_dict()
        else:
            data = {
                "error_type": type(error).__name__,
                "message": str(error),
                "location": "",
                "project_id": "",
                "stage": "",
                "cause": "",
                "suggested_fix": "",
                "created_at": _now_iso(),
            }
        if self._logger is not None:
            self._logger.error(data["message"], metadata=data)
        return data
