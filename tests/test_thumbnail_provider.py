# -*- coding: utf-8 -*-
"""Thumbnail provider 테스트.

규칙: 외부 API 호출 없음, 실제 runtime 산출물 생성 없음.
실행: 프로젝트 루트에서
  python -m unittest tests.test_thumbnail_provider -v
"""
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSValidationError  # noqa: E402
from providers import ThumbnailProvider  # noqa: E402

BRAND = {
    "thumbnail_style": {
        "base": "본편 채택 이미지 재활용 (텍스트 없는 원본)",
        "text_overlay": "한글 훅 문구 1줄, 굵은 산세리프",
        "color_accent": "시안/앰버 대비 — 채널 시그니처",
        "banned": "3줄 이상 텍스트, 형광색 남발, 낚시성 화살표",
    },
}

STRATEGY = {
    "thumbnail_hypotheses": [
        "2100년 서울의 아침 — 창밖 홀로그램",
        "식탁 위 배양육 한 접시",
    ],
    "title_hypotheses": ["2100년 서울의 아침"],
}


class TestThumbnailProviderSafety(unittest.TestCase):
    def test_placeholder_contract_matches_other_providers(self):
        provider = ThumbnailProvider()
        job = provider.create_job({"dummy": True})
        self.assertEqual(job["status"], "NOT_SUBMITTED")
        self.assertFalse(job["external_call_made"])
        self.assertTrue(provider.supports_manual_mode())
        instructions = provider.get_manual_instructions()
        self.assertEqual(instructions["mode"], "manual")
        self.assertFalse(instructions["external_call_made"])
        self.assertGreaterEqual(len(instructions["instructions"]), 3)

    def test_validate_config_allows_no_external_calls(self):
        config = ThumbnailProvider().validate_config()
        self.assertTrue(config["valid"])
        self.assertFalse(config["external_calls_allowed"])


class TestThumbnailWorkPack(unittest.TestCase):
    def setUp(self):
        self.provider = ThumbnailProvider()

    def test_one_item_per_hypothesis(self):
        pack = self.provider.build_work_pack(BRAND, STRATEGY)
        self.assertEqual(len(pack["items"]), 2)
        self.assertEqual(
            [item["hypothesis"] for item in pack["items"]],
            STRATEGY["thumbnail_hypotheses"],
        )
        self.assertEqual([item["index"] for item in pack["items"]], [1, 2])

    def test_pack_carries_brand_rules_verbatim(self):
        pack = self.provider.build_work_pack(BRAND, STRATEGY)
        self.assertEqual(pack["brand_rules"], BRAND["thumbnail_style"])

    def test_pack_is_manual_and_declares_no_external_call(self):
        pack = self.provider.build_work_pack(BRAND, STRATEGY)
        self.assertEqual(pack["export_mode"], "manual")
        self.assertFalse(pack["external_call_made"])
        self.assertIn("disclaimer", pack)
        self.assertGreaterEqual(len(pack["instructions"]), 3)

    def test_missing_thumbnail_style_raises(self):
        with self.assertRaises(ADOSValidationError):
            self.provider.build_work_pack({}, STRATEGY)

    def test_missing_hypotheses_raises(self):
        with self.assertRaises(ADOSValidationError):
            self.provider.build_work_pack(BRAND, {})

    def test_empty_hypotheses_raises_instead_of_inventing(self):
        """근거 없는 썸네일 안을 지어내지 않는다 — 빈 팩도 만들지 않는다."""
        with self.assertRaises(ADOSValidationError):
            self.provider.build_work_pack(BRAND, {"thumbnail_hypotheses": []})

    def test_blank_hypothesis_entry_raises(self):
        with self.assertRaises(ADOSValidationError):
            self.provider.build_work_pack(BRAND, {"thumbnail_hypotheses": ["  "]})


if __name__ == "__main__":
    unittest.main()
