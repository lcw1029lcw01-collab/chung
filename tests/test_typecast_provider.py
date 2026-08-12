# -*- coding: utf-8 -*-
"""Typecast provider 계약 테스트.

typecast는 수동 경로(ProviderInterface)와 실제 합성 경로를 함께 가진다.
이 테스트는 외부 API를 호출하지 않는다 — synthesize/list_voices는 부르지 않는다.

실행: 프로젝트 루트에서
  python -m unittest tests.test_typecast_provider -v
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from providers import PlaceholderProvider, TypecastProvider  # noqa: E402


class TestTypecastManualContract(unittest.TestCase):
    """WIP가 한 번 깨뜨렸던 계약 — 다시 깨지면 여기서 잡는다."""

    def test_still_a_provider_interface_member(self):
        self.assertIsInstance(TypecastProvider(), PlaceholderProvider)

    def test_create_job_submits_nothing(self):
        job = TypecastProvider().create_job({"text": "안녕하세요"})
        self.assertEqual(job["status"], "NOT_SUBMITTED")
        self.assertFalse(job["external_call_made"])

    def test_manual_instructions_point_at_the_script_pack(self):
        instructions = TypecastProvider().get_manual_instructions()
        self.assertEqual(instructions["mode"], "manual")
        self.assertGreaterEqual(len(instructions["instructions"]), 3)
        self.assertTrue(
            any("typecast_script_pack.json" in line for line in instructions["instructions"]),
            "ProviderExporter가 만드는 팩을 안내해야 한다",
        )


class TestTypecastDeclaresItsLivePath(unittest.TestCase):
    def test_validate_config_admits_external_calls(self):
        config = TypecastProvider().validate_config()
        self.assertTrue(config["valid"])
        self.assertTrue(config["external_calls_allowed"])
        self.assertEqual(
            sorted(config["external_call_methods"]), ["list_voices", "synthesize"]
        )


class TestTypecastApiKeyIsLazy(unittest.TestCase):
    """키가 없는 환경에서도 수동 경로는 살아 있어야 한다."""

    def test_construction_does_not_read_the_key(self):
        with mock.patch.object(
            TypecastProvider, "_load_key", side_effect=AssertionError("생성 시 키를 읽으면 안 된다")
        ):
            provider = TypecastProvider()
            provider.create_job({"text": "키 없이도 동작"})
            provider.get_manual_instructions()
        self.assertEqual(provider.provider_name, "typecast")

    def test_key_is_read_on_first_access(self):
        with mock.patch.object(TypecastProvider, "_load_key", return_value="k-test") as loader:
            provider = TypecastProvider()
            loader.assert_not_called()
            self.assertEqual(provider.api_key, "k-test")
            loader.assert_called_once()

    def test_explicit_key_is_never_looked_up(self):
        with mock.patch.object(
            TypecastProvider, "_load_key", side_effect=AssertionError("주입한 키를 무시하면 안 된다")
        ):
            self.assertEqual(TypecastProvider(api_key="k-given").api_key, "k-given")


if __name__ == "__main__":
    unittest.main()
