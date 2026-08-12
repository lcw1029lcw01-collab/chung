# -*- coding: utf-8 -*-
"""Video composition (자막 번인) 계층 테스트.

규칙: 임시 폴더만 사용. ffmpeg가 없으면 통합 테스트는 skip한다.
실행: 프로젝트 루트에서  python -m unittest tests.test_video_composition -v
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSFileNotFoundError, ADOSValidationError  # noqa: E402
from engines.composition import VideoComposer  # noqa: E402
from engines.composition.video_composer import DEFAULT_SUBTITLE_STYLE  # noqa: E402

DOCS_DIR = PROJECT_ROOT / "docs"
_DOCS_SNAPSHOT = sorted(
    (p.name, p.stat().st_size, p.stat().st_mtime_ns)
    for p in DOCS_DIR.rglob("*.md")
)

FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None

SAMPLE_SRT = """1
00:00:00,500 --> 00:00:02,000
첫 번째 자막입니다.

2
00:00:02,600 --> 00:00:03,800
두 번째 자막,
두 줄짜리.
"""


class SrtBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.composer = VideoComposer()

    def tearDown(self):
        self.tmp.cleanup()

    def write_srt(self, content: str, name: str = "subtitles_ko.srt") -> Path:
        path = self.tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path


class TestParseSrt(SrtBase):
    def test_parses_cues_with_times_and_text(self):
        srt = self.write_srt(SAMPLE_SRT)
        cues = self.composer.parse_srt(srt)
        self.assertEqual(len(cues), 2)
        self.assertAlmostEqual(cues[0]["start_seconds"], 0.5)
        self.assertAlmostEqual(cues[0]["end_seconds"], 2.0)
        self.assertEqual(cues[0]["text"], "첫 번째 자막입니다.")
        self.assertIn("두 줄짜리", cues[1]["text"])

    def test_parses_bom_and_crlf(self):
        # write_bytes로 정확한 CRLF+BOM 바이트를 만든다 (write_text는 \n을 \r\n로 재변환)
        srt = self.tmp_path / "subtitles_crlf.srt"
        srt.write_bytes(b"\xef\xbb\xbf" + SAMPLE_SRT.replace("\n", "\r\n").encode("utf-8"))
        cues = self.composer.parse_srt(srt)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0]["text"], "첫 번째 자막입니다.")

    def test_missing_file_raises(self):
        with self.assertRaises(ADOSFileNotFoundError):
            self.composer.parse_srt(self.tmp_path / "no_such.srt")


class TestValidateSubtitles(SrtBase):
    def test_pass_report(self):
        srt = self.write_srt(SAMPLE_SRT)
        report = self.composer.validate_subtitles(srt, video_duration_seconds=4.0)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["cue_count"], 2)
        self.assertAlmostEqual(report["coverage_ratio"], 0.95)

    def test_detects_overlap(self):
        overlapping = """1
00:00:00,000 --> 00:00:03,000
첫 큐

2
00:00:02,000 --> 00:00:04,000
겹치는 큐
"""
        srt = self.write_srt(overlapping)
        report = self.composer.validate_subtitles(srt)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("cue_2_overlaps_previous", report["issues"])

    def test_detects_cue_beyond_video_end(self):
        srt = self.write_srt(SAMPLE_SRT)
        report = self.composer.validate_subtitles(srt, video_duration_seconds=2.0)
        self.assertIn("last_cue_exceeds_video_duration", report["issues"])

    def test_empty_srt_fails(self):
        srt = self.write_srt("")
        report = self.composer.validate_subtitles(srt)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("no_cues", report["issues"])


class TestSubtitlesFilter(SrtBase):
    def test_filter_uses_relative_filename_and_style(self):
        # 고정값(MarginV=40) 검사 대신, 실제 전달한 style이 그대로 반영되는지 검증한다.
        filter_str = self.composer._subtitles_filter("subtitles_ko.srt", DEFAULT_SUBTITLE_STYLE)
        self.assertTrue(filter_str.startswith("subtitles=subtitles_ko.srt:force_style='"))
        for key, value in DEFAULT_SUBTITLE_STYLE.items():
            self.assertIn(f"{key}={value}", filter_str)
        # 한글 경로 함정 회피 — 필터에 드라이브 콜론/절대 경로 금지
        self.assertNotIn(":\\", filter_str)
        self.assertNotIn("C:/", filter_str)

    def test_filter_reflects_custom_style(self):
        custom = {"MarginV": "40", "Fontsize": "22"}
        filter_str = self.composer._subtitles_filter("s.srt", custom)
        self.assertIn("MarginV=40", filter_str)
        self.assertIn("Fontsize=22", filter_str)


@unittest.skipUnless(FFMPEG_AVAILABLE, "ffmpeg/ffprobe가 PATH에 없음")
class TestBurnIntegration(SrtBase):
    def make_base_clip(self, seconds: float = 4.0, color: str = "0x202020", name: str = "base.mp4") -> Path:
        base = self.tmp_path / name
        self.composer._run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"color=c={color}:s=640x360:d={seconds}:r=25",
                "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono:d={seconds}",
                "-c:v", "libx264", "-crf", "28", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest",
                str(base),
            ]
        )
        return base

    def test_burn_and_verify_subtitles_visible(self):
        base = self.make_base_clip()
        srt = self.write_srt(SAMPLE_SRT)
        out = self.tmp_path / "subtitled.mp4"
        self.composer.burn_subtitles(base, srt, out)
        self.assertTrue(out.is_file())
        base_duration = self.composer.probe_duration(base)
        out_duration = self.composer.probe_duration(out)
        self.assertLessEqual(abs(base_duration - out_duration), 0.2)
        report = self.composer.verify_burned_subtitles(base, out, srt, sample_cues=2)
        self.assertTrue(report["subtitles_visible"], f"자막 미감지: {report}")
        self.assertEqual(report["status"], "PASS")

    def test_verify_fails_on_video_without_subtitles(self):
        base = self.make_base_clip()
        srt = self.write_srt(SAMPLE_SRT)
        report = self.composer.verify_burned_subtitles(base, base, srt, sample_cues=2)
        self.assertFalse(report["subtitles_visible"], "무자막 영상인데 자막이 감지됨")
        self.assertEqual(report["status"], "FAIL")

    def test_verify_fails_on_bright_video_without_subtitles(self):
        # 리뷰 회귀: 밝은 배경(흰 화면)에서 밝기 휴리스틱은 자막 없이도 PASS였다.
        # 차분 방식은 번인이 없으면 배경 밝기와 무관하게 FAIL이어야 한다.
        white = self.make_base_clip(color="white", name="white.mp4")
        srt = self.write_srt(SAMPLE_SRT)
        report = self.composer.verify_burned_subtitles(white, white, srt, sample_cues=2)
        self.assertFalse(report["subtitles_visible"], "밝은 무자막 영상이 오탐으로 PASS됨")
        self.assertEqual(report["status"], "FAIL")

    def test_burn_detected_on_bright_video(self):
        # 흰 배경 + 흰 자막이라도 검은 외곽선이 차이를 만들어 감지돼야 한다
        white = self.make_base_clip(color="white", name="white_base.mp4")
        srt = self.write_srt(SAMPLE_SRT)
        out = self.tmp_path / "white_subtitled.mp4"
        self.composer.burn_subtitles(white, srt, out)
        report = self.composer.verify_burned_subtitles(white, out, srt, sample_cues=2)
        self.assertTrue(report["subtitles_visible"], f"밝은 배경에서 자막 미감지: {report}")

    def test_burn_requires_cues(self):
        base = self.make_base_clip(seconds=1.0)
        srt = self.write_srt("")
        with self.assertRaises(ADOSValidationError):
            self.composer.burn_subtitles(base, srt, self.tmp_path / "out.mp4")


class TestZDocsUntouched(unittest.TestCase):
    def test_docs_not_modified(self):
        snapshot = sorted(
            (p.name, p.stat().st_size, p.stat().st_mtime_ns)
            for p in DOCS_DIR.rglob("*.md")
        )
        self.assertEqual(snapshot, _DOCS_SNAPSHOT, "테스트가 docs/*.md를 변경함")


if __name__ == "__main__":
    unittest.main(verbosity=2)
