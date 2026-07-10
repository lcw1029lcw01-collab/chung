# -*- coding: utf-8 -*-
"""Midjourney Video provider placeholder.

Midjourney Video API를 호출하지 않는다. 영상을 생성하지 않는다.
"""
from .provider_interface import PlaceholderProvider


class MidjourneyVideoProvider(PlaceholderProvider):
    provider_name = "midjourney_video"
    provider_type = "video"
    not_implemented_reason = "Midjourney Video API integration not implemented."
    manual_instructions = [
        "providers/exports/midjourney_video_prompt_pack.json의 motion_prompt를 확인한다.",
        "해당 scene의 원본 이미지로 Midjourney Video 클립을 수동 생성한다.",
        "duration_seconds를 넘지 않게 저장 후 ProviderImporter로 등록한다.",
    ]
