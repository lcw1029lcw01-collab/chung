# -*- coding: utf-8 -*-
"""자막 번역 잡 계층 테스트 — 순수 함수만, 파일 IO는 임시 폴더만.

실행: 프로젝트 루트에서  python -m unittest tests.test_subtitle_translation -v
"""
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.composition.subtitle_translation import (  # noqa: E402
    assemble_srt,
    build_translation_job,
    format_srt_timestamp,
    validate_translated_srt,
    validate_translation_job,
)

CUES = [
    {"index": 1, "start_seconds": 0.0, "end_seconds": 4.2,
     "text": "서기 2100년, 인류는 선택의 기로에 섰습니다."},
    {"index": 2, "start_seconds": 4.2, "end_seconds": 9.87,
     "text": "이 이야기는 그 선택의 기록입니다."},
]


class TestBuildTranslationJob(unittest.TestCase):
    def test_job_structure_and_empty_slots(self):
        job = build_translation_job(CUES, ["en", "ja"])
        self.assertEqual(job["source_lang"], "ko")
        self.assertEqual(job["target_languages"], ["en", "ja"])
        self.assertEqual(job["cue_count"], 2)
        self.assertTrue(job["translation_notes"])
        first = job["cues"][0]
        self.assertEqual(first["index"], 1)
        self.assertEqual(first["source_text"], CUES[0]["text"])
        self.assertEqual(first["translations"], {"en": None, "ja": None})

    def test_existing_translations_preserved_by_index_and_text(self):
        old = build_translation_job(CUES, ["en"])
        old["cues"][0]["translations"]["en"] = "In the year 2100, ..."
        job = build_translation_job(CUES, ["en", "ja"], existing_job=old)
        self.assertEqual(job["cues"][0]["translations"]["en"], "In the year 2100, ...")
        self.assertIsNone(job["cues"][0]["translations"]["ja"])
        self.assertIsNone(job["cues"][1]["translations"]["en"])

    def test_changed_source_text_drops_stale_translation(self):
        old = build_translation_job(CUES, ["en"])
        old["cues"][0]["translations"]["en"] = "stale"
        changed = [dict(CUES[0], text="완전히 새로운 문장입니다."), CUES[1]]
        job = build_translation_job(changed, ["en"], existing_job=old)
        self.assertIsNone(job["cues"][0]["translations"]["en"])


class TestFormatSrtTimestamp(unittest.TestCase):
    def test_zero_and_plain(self):
        self.assertEqual(format_srt_timestamp(0), "00:00:00,000")
        self.assertEqual(format_srt_timestamp(1.5), "00:00:01,500")

    def test_hours_and_milliseconds(self):
        self.assertEqual(format_srt_timestamp(3661.007), "01:01:01,007")


class TestAssembleSrt(unittest.TestCase):
    def test_assemble_keeps_timecodes_and_renumbers(self):
        job = build_translation_job(CUES, ["en"])
        job["cues"][0]["translations"]["en"] = "In 2100, humanity stood at a crossroads."
        job["cues"][1]["translations"]["en"] = "This is the record of that choice."
        srt = assemble_srt(job, "en")
        blocks = srt.strip().split("\n\n")
        self.assertEqual(len(blocks), 2)
        self.assertEqual(
            blocks[0],
            "1\n00:00:00,000 --> 00:00:04,200\nIn 2100, humanity stood at a crossroads.",
        )
        self.assertEqual(
            blocks[1],
            "2\n00:00:04,200 --> 00:00:09,870\nThis is the record of that choice.",
        )
        self.assertTrue(srt.endswith("\n"))


class TestValidateTranslationJob(unittest.TestCase):
    def test_untranslated_cues_listed(self):
        job = build_translation_job(CUES, ["en", "ja"])
        job["cues"][0]["translations"]["en"] = "filled"
        report = validate_translation_job(job)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("en_untranslated_cues:[2]", report["issues"])
        self.assertIn("ja_untranslated_cues:[1, 2]", report["issues"])

    def test_complete_job_passes(self):
        job = build_translation_job(CUES, ["en"])
        for cue in job["cues"]:
            cue["translations"]["en"] = "ok"
        self.assertEqual(validate_translation_job(job)["status"], "PASS")


class TestValidateTranslatedSrt(unittest.TestCase):
    def translated(self, texts: list[str]) -> list[dict]:
        return [
            {"index": i + 1, "start_seconds": c["start_seconds"],
             "end_seconds": c["end_seconds"], "text": t}
            for i, (c, t) in enumerate(zip(CUES, texts))
        ]

    def test_pass_case(self):
        report = validate_translated_srt(
            CUES, self.translated(["In 2100...", "This is the record."]), "en")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["cue_count"], 2)

    def test_cue_count_mismatch(self):
        report = validate_translated_srt(CUES, self.translated(["only one"])[:1], "en")
        self.assertIn("cue_count_mismatch:2!=1", report["issues"])

    def test_timecode_drift_detected(self):
        cues = self.translated(["a", "b"])
        cues[1]["start_seconds"] += 0.05
        report = validate_translated_srt(CUES, cues, "en")
        self.assertIn("cue_2_timecode_mismatch", report["issues"])

    def test_empty_text_and_hangul_remains(self):
        report = validate_translated_srt(CUES, self.translated(["", "번역 안 됨"]), "en")
        self.assertIn("cue_1_empty_text", report["issues"])
        self.assertIn("cue_2_hangul_remains", report["issues"])

    def test_hangul_allowed_for_ko(self):
        report = validate_translated_srt(CUES, self.translated(["가나", "다라"]), "ko")
        self.assertEqual(report["status"], "PASS")


class TestRoundTrip(unittest.TestCase):
    def test_job_to_srt_to_parse_to_validate(self):
        import tempfile

        from engines.composition import VideoComposer

        job = build_translation_job(CUES, ["en"])
        job["cues"][0]["translations"]["en"] = "In 2100, humanity stood at a crossroads."
        job["cues"][1]["translations"]["en"] = "This is the record of that choice."
        srt_text = assemble_srt(job, "en")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "subtitles_en.srt"
            path.write_text(srt_text, encoding="utf-8")
            parsed = VideoComposer().parse_srt(path)
        report = validate_translated_srt(CUES, parsed, "en")
        self.assertEqual(report["status"], "PASS", report["issues"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
