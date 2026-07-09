# -*- coding: utf-8 -*-
"""Midjourney Video provider placeholder.

Midjourney Video API를 호출하지 않는다. 영상을 생성하지 않는다.
"""
from .provider_interface import PlaceholderProvider


class MidjourneyVideoProvider(PlaceholderProvider):
    provider_name = "midjourney_video"
    provider_type = "video"
    not_implemented_reason = "Midjourney Video API integration not implemented."
