# -*- coding: utf-8 -*-
"""Typecast provider placeholder.

Typecast API를 호출하지 않는다. 오디오를 생성하지 않는다.
"""
from .provider_interface import PlaceholderProvider


class TypecastProvider(PlaceholderProvider):
    provider_name = "typecast"
    provider_type = "voice"
    not_implemented_reason = "Typecast API integration not implemented."
