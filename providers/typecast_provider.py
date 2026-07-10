# -*- coding: utf-8 -*-
"""Typecast provider placeholder.

Typecast API를 호출하지 않는다. 오디오를 생성하지 않는다.
"""
from .provider_interface import PlaceholderProvider


class TypecastProvider(PlaceholderProvider):
    provider_name = "typecast"
    provider_type = "voice"
    not_implemented_reason = "Typecast API integration not implemented."
    manual_instructions = [
        "providers/exports/typecast_script_pack.json의 블록별 text를 Typecast에 붙여넣는다.",
        "voice_style에 맞는 보이스로 블록별 오디오를 생성해 저장한다.",
        "저장한 파일을 ProviderImporter로 메타데이터 등록 후 AssetRegistry에 연결한다.",
    ]
