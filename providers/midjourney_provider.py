# -*- coding: utf-8 -*-
"""Midjourney provider placeholder.

Midjourney API를 호출하지 않는다. 이미지를 생성하지 않는다.
"""
from .provider_interface import PlaceholderProvider


class MidjourneyProvider(PlaceholderProvider):
    provider_name = "midjourney"
    provider_type = "image"
    not_implemented_reason = "Midjourney API integration not implemented."
