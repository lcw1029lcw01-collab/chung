# -*- coding: utf-8 -*-
"""Typecast provider — 수동 작업 팩 + 신형 API(api.typecast.ai) 실제 호출.

두 경로를 가진다. 다른 provider와 달리 실제 외부 호출 경로가 있다.

1. 수동 경로 (기본, ProviderInterface 계약) — create_job/get_job_status/fetch_result는
   아무것도 제출하지 않는다. providers/exports/typecast_script_pack.json을 사람이
   Typecast에 붙여넣고 결과를 import한다.
2. 실제 합성 경로 — synthesize()/list_voices()만 api.typecast.ai를 호출한다.
   감독(사용자)이 scripts/generate_narration.py로 명시적으로 요청할 때만 쓴다.

API 키는 .env의 TYPECAST_API_KEY에서 읽는다 (코드/문서에 넣지 않는다).
키는 생성 시점이 아니라 **실제 호출 시점**에 읽는다 — 키가 없어도 수동 경로는 동작해야 한다.
업로드는 하지 않는다.
"""
import os
import time
from pathlib import Path

from .provider_interface import PlaceholderProvider

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

API_BASE = "https://api.typecast.ai"
DEFAULT_MODEL = "ssfm-v30"


class TypecastError(RuntimeError):
    pass


class TypecastProvider(PlaceholderProvider):
    provider_name = "typecast"
    provider_type = "voice"
    not_implemented_reason = (
        "create_job은 제출하지 않는다 — 실제 합성은 synthesize()로만 수행한다."
    )
    manual_instructions = [
        "providers/exports/typecast_script_pack.json의 블록별 text를 Typecast에 붙여넣는다.",
        "voice_style에 맞는 보이스로 블록별 오디오를 생성해 저장한다.",
        "저장한 파일을 ProviderImporter로 메타데이터 등록 후 AssetRegistry에 연결한다.",
    ]

    def __init__(self, api_key: str | None = None):
        super().__init__()
        self._api_key = api_key

    @property
    def api_key(self) -> str:
        """실제 호출 직전에만 키를 읽는다."""
        if not self._api_key:
            self._api_key = self._load_key()
        return self._api_key

    def validate_config(self) -> dict:
        """placeholder 형제들과 달리 실제 호출 경로가 있다 — 숨기지 않는다."""
        config = super().validate_config()
        config["external_calls_allowed"] = True
        config["external_call_methods"] = ["list_voices", "synthesize"]
        return config

    @staticmethod
    def _load_key() -> str:
        key = os.environ.get("TYPECAST_API_KEY")
        if key:
            return key
        # .env 폴백 (프로젝트 루트 탐색)
        for base in (Path.cwd(), *Path.cwd().parents):
            env = base / ".env"
            if env.is_file():
                for line in env.read_text(encoding="utf-8").splitlines():
                    if line.startswith("TYPECAST_API_KEY="):
                        return line.split("=", 1)[1].strip()
        raise TypecastError(
            "TYPECAST_API_KEY가 없습니다 — .env 또는 환경변수에 설정하세요."
        )

    def _headers(self) -> dict:
        return {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

    def list_voices(self) -> list[dict]:
        if requests is None:
            raise TypecastError("requests 패키지가 필요합니다: pip install requests")
        resp = requests.get(f"{API_BASE}/v1/voices", headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def synthesize(
        self,
        text: str,
        voice_id: str,
        out_path: str | Path,
        emotion: str = "normal",
        model: str = DEFAULT_MODEL,
        retries: int = 3,
    ) -> Path:
        """텍스트를 wav로 합성해 out_path에 저장한다."""
        if requests is None:
            raise TypecastError("requests 패키지가 필요합니다: pip install requests")
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "voice_id": voice_id,
            "text": text,
            "model": model,
            "emotion": emotion,
        }
        last_error = None
        for attempt in range(1, retries + 1):
            try:
                resp = requests.post(
                    f"{API_BASE}/v1/text-to-speech",
                    headers=self._headers(),
                    json=payload,
                    timeout=90,
                )
                if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("audio"):
                    out_path.write_bytes(resp.content)
                    return out_path
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
            time.sleep(2 * attempt)
        raise TypecastError(f"합성 실패 ({voice_id}): {last_error}")
