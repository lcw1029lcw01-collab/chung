# -*- coding: utf-8 -*-
"""Thumbnail provider — 썸네일 수동 작업 팩 생성.

썸네일 생성 API를 호출하지 않는다. 이미지를 만들지 않는다.
채널 brand_profile의 thumbnail_style과 content_strategy의 thumbnail_hypotheses를
하나의 작업 팩으로 합쳐, 사람이 무엇을 만들어야 하는지 확정한다.

근거가 없으면 팩을 만들지 않는다 — 썸네일 안을 지어내지 않는다.
"""
from datetime import datetime, timezone

from core import ADOSValidationError

from .provider_interface import PlaceholderProvider

DISCLAIMER = (
    "Manual work pack. Nothing was submitted externally. "
    "external_call_made is always false."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ThumbnailProvider(PlaceholderProvider):
    provider_name = "thumbnail"
    provider_type = "thumbnail"
    not_implemented_reason = "Thumbnail generation API integration not implemented."
    manual_instructions = [
        "providers/exports/thumbnail_prompt_pack.json의 brand_rules를 먼저 읽는다.",
        "items의 각 hypothesis마다 썸네일 후보를 1장씩 만든다 (banned 항목 위반 금지).",
        "만든 파일을 ManualAssetImporter로 등록한 뒤 AssetRegistry에 연결한다.",
    ]

    def build_work_pack(self, brand_profile: dict, content_strategy: dict) -> dict:
        """brand_profile + content_strategy → 썸네일 작업 팩.

        brand_profile: 채널 brand_profile.yaml을 읽은 dict.
        content_strategy: longform.strategy가 만든 research/content_strategy.json.
        """
        brand_rules = (brand_profile or {}).get("thumbnail_style")
        if not isinstance(brand_rules, dict) or not brand_rules:
            raise ADOSValidationError(
                "brand_profile에 thumbnail_style이 없습니다.",
                location="ThumbnailProvider.build_work_pack",
                suggested_fix="channels/<channel_id>/brand_profile.yaml에 thumbnail_style을 정의하세요.",
            )

        hypotheses = (content_strategy or {}).get("thumbnail_hypotheses")
        if not isinstance(hypotheses, list) or not hypotheses:
            raise ADOSValidationError(
                "content_strategy에 thumbnail_hypotheses가 없습니다.",
                location="ThumbnailProvider.build_work_pack",
                suggested_fix="CONTENT_STRATEGY 단계 결과를 먼저 import하세요.",
            )

        items = []
        for index, hypothesis in enumerate(hypotheses, start=1):
            if not isinstance(hypothesis, str) or hypothesis.strip() == "":
                raise ADOSValidationError(
                    f"thumbnail_hypotheses[{index - 1}]가 비어 있습니다.",
                    location="ThumbnailProvider.build_work_pack",
                    suggested_fix="빈 항목을 지우거나 실제 썸네일 안을 채우세요.",
                )
            items.append({"index": index, "hypothesis": hypothesis})

        return {
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "export_mode": "manual",
            "external_call_made": False,
            "instructions": list(self.manual_instructions),
            "brand_rules": dict(brand_rules),
            "title_hypotheses": list(content_strategy.get("title_hypotheses") or []),
            "items": items,
            "created_at": _now_iso(),
            "disclaimer": DISCLAIMER,
        }
