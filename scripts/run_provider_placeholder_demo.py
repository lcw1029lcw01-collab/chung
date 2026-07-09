# -*- coding: utf-8 -*-
"""Provider placeholder 데모.

Midjourney / Midjourney Video / Typecast placeholder에 더미 요청을 하나씩
보내고, 외부 호출이 전혀 없었음을 확인한다.

실행: 프로젝트 루트에서  python scripts/run_provider_placeholder_demo.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from providers import (  # noqa: E402
    MidjourneyProvider,
    MidjourneyVideoProvider,
    TypecastProvider,
)


def main() -> int:
    requests = {
        "midjourney": {"prompt": "cinematic future city (placeholder)"},
        "midjourney_video": {"source_image": None, "motion": "slow push-in (placeholder)"},
        "typecast": {"text": "안녕하세요, 충컴퍼니입니다. (placeholder)", "voice": "narrator"},
    }
    providers = [MidjourneyProvider(), MidjourneyVideoProvider(), TypecastProvider()]

    print(f"{'provider_name':<18}{'type':<8}{'status':<15}{'external_call_made'}")
    for provider in providers:
        job = provider.create_job(requests[provider.provider_name])
        print(
            f"{job['provider_name']:<18}{job['provider_type']:<8}"
            f"{job['status']:<15}{job['external_call_made']}"
        )
    print()
    print("외부 API 호출 없음 — 모든 provider는 placeholder 모드(NOT_SUBMITTED)입니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
