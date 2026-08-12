# -*- coding: utf-8 -*-
"""자막 스타일(프리셋 해석 + ASS 생성) 테스트.

규칙: 순수 함수 + 임시 파일만. ffmpeg 불필요.
실행: 프로젝트 루트에서  python -m unittest tests.test_subtitle_style -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSConfigError  # noqa: E402
from engines.composition.subtitle_style import (  # noqa: E402
    build_ass,
    load_styles,
    resolve_style,
)

STYLES = {
    "default": {"FontName": "Malgun Gothic", "Fontsize": 50, "MarginV": 70,
                "max_chars_per_line": 16, "max_lines": 2},
    "presets": {
        "documentary": {"Bold": 1, "BorderStyle": 1},
        "punchy": {"Fontsize": 56, "BorderStyle": 3},
    },
}


def rcue(start, end, lines, index=1):
    return {"index": index, "start_seconds": start, "end_seconds": end,
            "lines": lines, "text": "\n".join(lines)}


class TestResolveStyle(unittest.TestCase):
    def test_default_under_preset(self):
        style = resolve_style(STYLES, "documentary")
        self.assertEqual(style["FontName"], "Malgun Gothic")  # default 상속
        self.assertEqual(style["Bold"], 1)  # preset

    def test_overrides_win(self):
        style = resolve_style(STYLES, "documentary", {"Fontsize": 40})
        self.assertEqual(style["Fontsize"], 40)

    def test_unknown_preset_raises(self):
        with self.assertRaises(ADOSConfigError):
            resolve_style(STYLES, "nope")


class TestBuildAss(unittest.TestCase):
    def setUp(self):
        self.style = resolve_style(STYLES, "documentary")

    def test_header_sets_full_hd_playres(self):
        ass = build_ass([rcue(0.0, 2.4, ["2100년."])], self.style)
        self.assertIn("PlayResX: 1920", ass)
        self.assertIn("PlayResY: 1080", ass)
        self.assertIn("[V4+ Styles]", ass)
        self.assertIn("[Events]", ass)

    def test_style_line_carries_font(self):
        ass = build_ass([rcue(0.0, 2.4, ["2100년."])], self.style)
        style_line = next(l for l in ass.splitlines() if l.startswith("Style:"))
        self.assertIn("Malgun Gothic", style_line)
        self.assertIn("50", style_line)

    def test_two_line_cue_uses_hard_break(self):
        ass = build_ass([rcue(0.0, 3.0, ["지금이, 인류 역사상 가장", "공정한 시대라고 말합니다."])],
                        self.style)
        dialogue = next(l for l in ass.splitlines() if l.startswith("Dialogue:"))
        self.assertIn(r"\N", dialogue)
        self.assertIn("지금이, 인류 역사상 가장", dialogue)

    def test_time_format(self):
        ass = build_ass([rcue(0.0, 2.4, ["끝."])], self.style)
        dialogue = next(l for l in ass.splitlines() if l.startswith("Dialogue:"))
        self.assertIn("0:00:00.00", dialogue)
        self.assertIn("0:00:02.40", dialogue)

    def test_one_dialogue_per_cue(self):
        cues = [rcue(0.0, 1.0, ["가."], 1), rcue(1.0, 2.0, ["나."], 2)]
        ass = build_ass(cues, self.style)
        dialogues = [l for l in ass.splitlines() if l.startswith("Dialogue:")]
        self.assertEqual(len(dialogues), 2)


class TestLoadStyles(unittest.TestCase):
    def test_loads_yaml_with_presets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "subtitle_styles.yaml"
            path.write_text(
                "default:\n  FontName: Malgun Gothic\n  Fontsize: 50\n"
                "presets:\n  documentary:\n    Bold: 1\n",
                encoding="utf-8",
            )
            styles = load_styles(path)
            self.assertIn("documentary", styles["presets"])
            self.assertEqual(styles["default"]["Fontsize"], 50)


if __name__ == "__main__":
    unittest.main()
