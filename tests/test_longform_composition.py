# -*- coding: utf-8 -*-
"""Longform composition 실행기 테스트.

단위 테스트는 fake composer로 ffmpeg 없이 검증하고,
통합 테스트는 ffmpeg가 있을 때만 실행한다.

실행: 프로젝트 루트에서  python -m unittest tests.test_longform_composition -v
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSFileNotFoundError, ADOSValidationError  # noqa: E402
from engines.composition import LongformCompositionExecutor  # noqa: E402

FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None

STYLES = {
    "default": {"FontName": "Malgun Gothic", "Fontsize": 50, "max_chars_per_line": 16,
                "max_lines": 2},
    "presets": {
        "documentary": {"Fontsize": 70, "MarginV": 70},
        "custom_preset": {"Fontsize": 33, "MarginV": 44},
    },
}


class FakeComposer:
    """ffmpeg를 실행하지 않는 기록용 composer."""

    def __init__(self):
        self.ffmpeg = "ffmpeg"
        self.commands = []
        self.burn_style = None
        self.burn_cues = None

    def _run(self, cmd, cwd=None):
        self.commands.append(cmd)

    def probe_duration(self, path):
        return 2.0

    def concat_from_lists(self, build_dir, output_path, **kwargs):
        Path(output_path).write_bytes(b"\x00")
        return Path(output_path)

    def burn_subtitles_from_cues(self, video_path, cues, style, output_path, **kwargs):
        self.burn_style = dict(style)
        self.burn_cues = list(cues)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(b"\x00")
        return Path(output_path)

    def verify_burned_subtitles(self, base, out, srt, sample_cues=6):
        return {"subtitles_visible": True, "status": "PASS"}


class CompositionBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name)
        self.assets = self.proj / "assets" / "production"
        (self.assets / "audio").mkdir(parents=True)
        (self.assets / "images").mkdir(parents=True)
        (self.assets / "audio" / "b1.wav").write_bytes(b"\x00" * 32)
        (self.assets / "images" / "c1.png").write_bytes(b"\x00" * 32)
        self.fake = FakeComposer()
        self.executor = LongformCompositionExecutor(composer=self.fake)

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self, **overrides):
        data = {
            "assets_root": "assets/production",
            "fps": 25,
            "blocks": [{"id": "b1", "text": "첫 블록 나레이션 문장입니다",
                        "audio": "audio/b1.wav",
                        "cuts": [{"id": "c1", "image": "images/c1.png", "kb": "zi"}]}],
        }
        data.update(overrides)
        return data


class TestManifestValidation(CompositionBase):
    def test_absolute_asset_path_rejected(self):
        manifest = self.manifest()
        manifest["blocks"][0]["audio"] = str(self.assets / "audio" / "b1.wav")  # 절대 경로
        with self.assertRaises(ADOSValidationError):
            self.executor.validate_manifest(self.proj, manifest)

    def test_absolute_assets_root_rejected(self):
        manifest = self.manifest(assets_root=str(self.assets))
        with self.assertRaises(ADOSValidationError):
            self.executor.validate_manifest(self.proj, manifest)

    def test_path_escape_rejected(self):
        manifest = self.manifest()
        manifest["blocks"][0]["cuts"][0]["image"] = "../../outside.png"
        with self.assertRaises(ADOSValidationError):
            self.executor.validate_manifest(self.proj, manifest)

    def test_missing_assets_fail_with_list(self):
        manifest = self.manifest()
        manifest["blocks"][0]["cuts"].append({"id": "c2", "image": "images/none.png"})
        with self.assertRaises(ADOSFileNotFoundError) as caught:
            self.executor.validate_manifest(self.proj, manifest)
        self.assertIn("none.png", caught.exception.message)

    def test_empty_cuts_rejected(self):
        manifest = self.manifest()
        manifest["blocks"][0]["cuts"] = []
        with self.assertRaises(ADOSValidationError):
            self.executor.validate_manifest(self.proj, manifest)


class TestComposeGuards(CompositionBase):
    def test_existing_output_not_overwritten_without_force(self):
        output_rel = "assets/video/final.mp4"
        out = self.proj / output_rel
        out.parent.mkdir(parents=True)
        out.write_bytes(b"EXISTING")
        with self.assertRaises(ADOSValidationError):
            self.executor.compose(self.proj, self.manifest(), {}, STYLES,
                                  output_rel=output_rel)
        self.assertEqual(out.read_bytes(), b"EXISTING")  # 원본 보존

    def test_force_allows_overwrite(self):
        output_rel = "assets/video/final.mp4"
        out = self.proj / output_rel
        out.parent.mkdir(parents=True)
        out.write_bytes(b"EXISTING")
        report = self.executor.compose(self.proj, self.manifest(), {}, STYLES,
                                       output_rel=output_rel, force=True)
        self.assertEqual(report["status"], "PASS")

    def test_channel_subtitle_preset_used(self):
        """채널 brand_profile의 preset + overrides가 번인 스타일에 반영된다."""
        brand = {"subtitle_style": "custom_preset", "subtitle_overrides": {"MarginV": 99}}
        report = self.executor.compose(self.proj, self.manifest(), brand, STYLES,
                                       output_rel="assets/video/out.mp4")
        self.assertEqual(report["subtitle_preset"], "custom_preset")
        self.assertEqual(self.fake.burn_style["Fontsize"], 33)   # preset 값
        self.assertEqual(self.fake.burn_style["MarginV"], 99)    # override 값
        self.assertEqual(self.fake.burn_style["FontName"], "Malgun Gothic")  # default 값

    def test_unknown_preset_fails(self):
        brand = {"subtitle_style": "ghost_preset"}
        with self.assertRaises(Exception):
            self.executor.compose(self.proj, self.manifest(), brand, STYLES,
                                  output_rel="assets/video/out.mp4")

    def test_report_counts(self):
        report = self.executor.compose(self.proj, self.manifest(), {}, STYLES,
                                       output_rel="assets/video/out.mp4")
        self.assertEqual(report["block_count"], 1)
        self.assertEqual(report["segment_count"], 1)
        self.assertEqual(report["block_cue_count"], 1)
        self.assertGreaterEqual(report["display_cue_count"], 1)
        self.assertTrue(report["verified"])


@unittest.skipUnless(FFMPEG_AVAILABLE, "ffmpeg/ffprobe가 PATH에 없음")
class TestComposeIntegration(unittest.TestCase):
    """실제 ffmpeg로 아주 작은 합성 1건 — 자막 가시성까지 검증."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name)
        assets = self.proj / "assets" / "production"
        (assets / "audio").mkdir(parents=True)
        (assets / "images").mkdir(parents=True)
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x303030:s=640x360:d=1",
             "-frames:v", "1", str(assets / "images" / "c1.png")],
            check=True, capture_output=True)
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=300:duration=1.2",
             "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le",
             str(assets / "audio" / "b1.wav")],
            check=True, capture_output=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_small_real_composition(self):
        executor = LongformCompositionExecutor()
        report = executor.compose(
            self.proj,
            {"assets_root": "assets/production", "fps": 25,
             "blocks": [{"id": "b1", "text": "미래 도시의 아침",
                         "audio": "audio/b1.wav",
                         "cuts": [{"id": "c1", "image": "images/c1.png", "kb": "zi"}]}]},
            {"subtitle_style": "documentary"},
            STYLES,
            output_rel="assets/video/final_test.mp4",
        )
        self.assertEqual(report["status"], "PASS", report)
        self.assertTrue(report["subtitles_visible"])
        self.assertTrue((self.proj / "assets/video/final_test.mp4").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
