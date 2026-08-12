# -*- coding: utf-8 -*-
"""자막 리플로우(내용 최적화) 테스트.

규칙: 순수 함수. ffmpeg 불필요.
실행: 프로젝트 루트에서  python -m unittest tests.test_subtitle_reflow -v
"""
import re
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.composition.subtitle_reflow import (  # noqa: E402
    char_width,
    reading_speed_warnings,
    reflow_cues,
)


def cue(start, end, text, index=1):
    return {"index": index, "start_seconds": start, "end_seconds": end, "text": text}


def widths_ok(lines, limit):
    return all(char_width(line) <= limit for line in lines)


class TestCharWidth(unittest.TestCase):
    def test_korean_is_one_latin_and_space_are_half(self):
        self.assertAlmostEqual(char_width("가나다"), 3.0)
        self.assertAlmostEqual(char_width("ab "), 1.5)  # 0.5 * 3
        self.assertAlmostEqual(char_width("가,"), 1.5)  # 한글 1 + 문장부호 0.5


class TestReflowShort(unittest.TestCase):
    def test_short_sentence_stays_one_line(self):
        out = reflow_cues([cue(0.0, 2.4, "2100년.")])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["lines"], ["2100년."])
        self.assertEqual(out[0]["text"], "2100년.")

    def test_preserves_timing(self):
        out = reflow_cues([cue(1.5, 3.75, "짧은 문장.")])
        self.assertAlmostEqual(out[0]["start_seconds"], 1.5)
        self.assertAlmostEqual(out[0]["end_seconds"], 3.75)


class TestReflowWrap(unittest.TestCase):
    def test_long_sentence_wraps_into_two_lines(self):
        text = "지금이, 인류 역사상 가장 공정한 시대라고 말합니다."
        out = reflow_cues([cue(0.0, 3.0, text)], max_chars_per_line=16, max_lines=2)
        self.assertEqual(len(out), 1)
        self.assertEqual(len(out[0]["lines"]), 2)
        self.assertTrue(widths_ok(out[0]["lines"], 16))

    def test_never_splits_a_word(self):
        text = "그리고 정부를 더 이상 믿지 못하게 된 순간부터"
        out = reflow_cues([cue(0.0, 3.0, text)])
        rejoined = " ".join(w for line in out[0]["lines"] for w in line.split())
        self.assertEqual(rejoined, text)  # 모든 단어 온전히 보존, 순서 유지

    def test_wrap_never_exceeds_line_limit(self):
        text = "사람들은 그것을 거버넌스라고 부르며 인간이 아니라 시스템이 결정합니다."
        out = reflow_cues([cue(0.0, 4.0, text)], max_chars_per_line=16, max_lines=2)
        for c in out:
            self.assertTrue(widths_ok(c["lines"], 16), c["lines"])


class TestReflowCueSplit(unittest.TestCase):
    def test_over_two_lines_splits_into_multiple_cues(self):
        # 32자 폭을 크게 넘겨 2줄로 안 담기는 큐
        text = ("이 나라의 모든 결정은 인간이 아니라 하나의 거대한 시스템이 내리고 "
                "사람들은 그것을 공정하다고 믿으며 지금이 가장 좋은 시대라 말합니다.")
        out = reflow_cues([cue(10.0, 20.0, text)], max_chars_per_line=16, max_lines=2)
        self.assertGreater(len(out), 1)
        # 시간 순서·경계 보존
        self.assertAlmostEqual(out[0]["start_seconds"], 10.0)
        self.assertAlmostEqual(out[-1]["end_seconds"], 20.0)
        for prev, cur in zip(out, out[1:]):
            self.assertLessEqual(prev["end_seconds"], cur["start_seconds"] + 1e-6)
        # 각 큐는 최대 2줄, 줄당 16자 이하
        for c in out:
            self.assertLessEqual(len(c["lines"]), 2)
            self.assertTrue(widths_ok(c["lines"], 16), c["lines"])

    def test_reindexes_output_cues(self):
        text = ("이 나라의 모든 결정은 인간이 아니라 하나의 거대한 시스템이 내리고 "
                "사람들은 그것을 공정하다고 믿으며 지금이 가장 좋은 시대라 말합니다.")
        out = reflow_cues([cue(10.0, 20.0, text)])
        self.assertEqual([c["index"] for c in out], list(range(1, len(out) + 1)))


class TestReflowSentenceAware(unittest.TestCase):
    def test_short_sentences_each_own_cue(self):
        # 한 큐의 두 짧은 문장 → 문장별로 분리 (병합 금지)
        out = reflow_cues([cue(0.0, 3.0, "2100년. 놀랍습니다.")])
        self.assertEqual([c["text"] for c in out], ["2100년.", "놀랍습니다."])

    def test_never_merges_across_sentence_boundary(self):
        text = "시청도, 세무서도, 경찰서도 그대로 있습니다. 다만 그 안에 사람이 없을 뿐입니다."
        out = reflow_cues([cue(0.0, 6.0, text)], max_chars_per_line=16, max_lines=2)
        self.assertGreaterEqual(len(out), 2)
        # 어떤 표시 큐도 마침표 뒤에 다음 문장이 붙지 않아야 한다
        for c in out:
            joined = c["text"].replace("\n", " ")
            self.assertIsNone(re.search(r"[.?!]\s*\S", joined), f"문장 병합됨: {joined}")

    def test_long_single_sentence_still_splits(self):
        text = "이 나라의 모든 결정은 인간이 아니라 하나의 거대한 시스템이 내리고 사람들은 그것을 공정하다고 믿습니다."
        out = reflow_cues([cue(0.0, 5.0, text)], max_chars_per_line=16, max_lines=2)
        self.assertGreater(len(out), 1)
        for c in out:
            self.assertTrue(widths_ok(c["lines"], 16), c["lines"])

    def test_question_and_exclamation_boundaries(self):
        out = reflow_cues([cue(0.0, 4.0, "왜일까요? 정말 그렇습니다!")])
        self.assertEqual([c["text"] for c in out], ["왜일까요?", "정말 그렇습니다!"])


class TestReadingSpeed(unittest.TestCase):
    def test_flags_too_fast_cue(self):
        # 20자를 1초에 → 20 cps > 12 cps
        out = reflow_cues([cue(0.0, 1.0, "인류 역사상 가장 공정한 시대라고 봅니다.")])
        warnings = reading_speed_warnings(out, max_cps=12)
        self.assertTrue(any(w["cue_index"] == out[0]["index"] for w in warnings))

    def test_comfortable_cue_not_flagged(self):
        out = reflow_cues([cue(0.0, 3.0, "짧은 문장.")])
        self.assertEqual(reading_speed_warnings(out, max_cps=12), [])


if __name__ == "__main__":
    unittest.main()
