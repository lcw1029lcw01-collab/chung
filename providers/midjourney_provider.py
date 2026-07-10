# -*- coding: utf-8 -*-
"""Midjourney provider placeholder.

Midjourney API를 호출하지 않는다. 이미지를 생성하지 않는다.
"""
from .provider_interface import PlaceholderProvider


class MidjourneyProvider(PlaceholderProvider):
    provider_name = "midjourney"
    provider_type = "image"
    not_implemented_reason = "Midjourney API integration not implemented."
    manual_instructions = [
        "providers/exports/midjourney_prompt_pack.json의 프롬프트를 Midjourney에 붙여넣는다.",
        "scene별 required_image_count만큼 이미지를 생성해 저장한다.",
        "저장한 파일을 ProviderImporter로 메타데이터 등록 후 AssetRegistry에 연결한다.",
    ]
