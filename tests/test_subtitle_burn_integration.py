# -*- coding: utf-8 -*-
"""ASS 자막 번인 통합 테스트 (리플로우 → 프리셋 해석 → ASS 번인 → 감지).

ffmpeg가 PATH에 없으면 skip한다.
실행: 프로젝트 루트에서  python -m unittest tests.test_subtitle_burn_integration -v
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.composition import VideoComposer  # noqa: E402
from engines.composition.subtitle_reflow import reflow_cues  # noqa: E402
from engines.composition.subtitle_style import load_styles, resolve_style  # noqa: E402

FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
STYLES_PATH = PROJECT_ROOT / "config" / "subtitle_styles.yaml"


@unittest.skipUnless(FFMPEG_AVAILABLE, "ffmpeg/ffprobe가 PATH에 없음")
class TestBurnFromCues(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.composer = VideoComposer()

    def tearDown(self):
        self.tmp.cleanup()

    def make_base_clip(self, seconds: float = 4.0, name: str = "base.mp4") -> Path:
        base = self.tmp_path / name
        self.composer._run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"color=c=0x202020:s=1280x720:d={seconds}:r=25",
                "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono:d={seconds}",
                "-c:v", "libx264", "-crf", "28", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest", str(base),
            ]
        )
        return base

    def test_burns_reflowed_cues_and_subtitles_detected(self):
        base = self.make_base_clip()
        raw = [
            {"index": 1, "start_seconds": 0.3, "end_seconds": 2.0, "text": "2100년."},
            {"index": 2, "start_seconds": 2.0, "end_seconds": 3.8,
             "text": "지금이, 인류 역사상 가장 공정한 시대라고 말합니다."},
        ]
        cues = reflow_cues(raw, max_chars_per_line=16, max_lines=2)
        style = resolve_style(load_styles(STYLES_PATH), "documentary")
        out = self.tmp_path / "subtitled.mp4"

        self.composer.burn_subtitles_from_cues(base, cues, style, out)

        self.assertTrue(out.is_file())
        # 길이 보존
        self.assertLessEqual(
            abs(self.composer.probe_duration(base) - self.composer.probe_duration(out)), 0.3
        )
        # 자막 픽셀이 실제로 렌더됐는지 (긴 큐 중간 시점)
        mid = (cues[-1]["start_seconds"] + cues[-1]["end_seconds"]) / 2
        diff = self.composer._bottom_band_diff(base, out, mid)
        self.assertGreaterEqual(diff, self.composer.SUBTITLE_DIFF_THRESHOLD, f"자막 미감지 diff={diff}")

    def test_written_ass_is_full_hd(self):
        base = self.make_base_clip(seconds=2.0)
        cues = reflow_cues(
            [{"index": 1, "start_seconds": 0.3, "end_seconds": 1.8, "text": "끝."}]
        )
        style = resolve_style(load_styles(STYLES_PATH), "documentary")
        out = self.tmp_path / "out.mp4"
        self.composer.burn_subtitles_from_cues(base, cues, style, out, ass_name="subs.ass")
        ass_text = (self.tmp_path / "subs.ass").read_text(encoding="utf-8-sig")
        self.assertIn("PlayResX: 1920", ass_text)
        self.assertIn("PlayResY: 1080", ass_text)


if __name__ == "__main__":
    unittest.main()
