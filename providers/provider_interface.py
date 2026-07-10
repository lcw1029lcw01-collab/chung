# -*- coding: utf-8 -*-
"""Provider interface (walking skeleton).

Engine → Provider Interface → Adapter 규칙(docs/14_PROVIDER_ENGINE.md)의
최소 인터페이스. 외부 API 호출은 없다.
"""
from datetime import datetime, timezone

from core import ADOSEngineError


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProviderInterface:
    """모든 Provider의 베이스. 기본 동작은 안전한 미구현 에러."""

    provider_name: str = "base"
    provider_type: str = "none"
    mode: str = "not_implemented"

    def validate_config(self) -> dict:
        return {
            "provider_name": self.provider_name,
            "valid": False,
            "reason": "NOT_IMPLEMENTED",
        }

    def create_job(self, request: dict) -> dict:
        raise ADOSEngineError(
            f"{self.provider_name} provider는 아직 구현되지 않았다.",
            location=f"{type(self).__name__}.create_job",
            suggested_fix="placeholder provider를 사용하거나 실제 adapter 구현 후 호출하세요.",
        )

    def get_job_status(self, job_id: str) -> dict:
        raise ADOSEngineError(
            f"{self.provider_name} provider는 아직 구현되지 않았다.",
            location=f"{type(self).__name__}.get_job_status",
        )

    def fetch_result(self, job_id: str) -> dict:
        raise ADOSEngineError(
            f"{self.provider_name} provider는 아직 구현되지 않았다.",
            location=f"{type(self).__name__}.fetch_result",
        )


class PlaceholderProvider(ProviderInterface):
    """외부 호출 없이 NOT_SUBMITTED 기록만 돌려주는 placeholder 공통 구현."""

    mode = "placeholder"
    not_implemented_reason = "Provider API integration not implemented."
    manual_instructions: list = []

    def __init__(self):
        self._job_counter = 0

    def supports_manual_mode(self) -> bool:
        """v0.2 수동 통합 워크플로우 지원 여부 (docs/32)."""
        return True

    def get_manual_instructions(self) -> dict:
        return {
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "mode": "manual",
            "external_call_made": False,
            "instructions": list(self.manual_instructions),
        }

    def validate_config(self) -> dict:
        return {
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "mode": self.mode,
            "valid": True,
            "external_calls_allowed": False,
        }

    def create_job(self, request: dict) -> dict:
        self._job_counter += 1
        return {
            "job_id": f"job-{self.provider_name}-{self._job_counter:04d}",
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "mode": self.mode,
            "status": "NOT_SUBMITTED",
            "external_call_made": False,
            "reason": self.not_implemented_reason,
            "request_echo": request,
            "created_at": _now_iso(),
        }

    def get_job_status(self, job_id: str) -> dict:
        return {
            "job_id": job_id,
            "provider_name": self.provider_name,
            "status": "NOT_SUBMITTED",
            "external_call_made": False,
        }

    def fetch_result(self, job_id: str) -> dict:
        return {
            "job_id": job_id,
            "provider_name": self.provider_name,
            "status": "NOT_AVAILABLE",
            "result": None,
            "external_call_made": False,
        }
