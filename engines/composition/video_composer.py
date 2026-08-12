# -*- coding: utf-8 -*-
"""Video composer (composition layer v1).

세그먼트 concat → 나레이션 mux → 자막 번인(burn-in)까지 실제 최종 영상을
조립한다. 지금까지 자막이 최종 영상에 나오지 않던 원인은 합성 단계가
시스템 밖(ad-hoc)에 있어 자막 번인이 통째로 빠졌기 때문이다.
근거: docs/36_VIDEO_COMPOSITION_V1.md

주의:
- ffmpeg/ffprobe 로컬 실행만 사용한다. 업로드·외부 API 호출 없음.
- Windows 한글 경로에서 subtitles 필터가 깨지지 않도록, 항상 srt가 있는
  폴더를 cwd로 삼아 상대 파일명으로 필터를 구성한다.
- 번인 후에는 검증(길이 일치 + 자막 구간 프레임 밝기)을 통과해야 한다.
"""
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSEngineError,
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSValidationError,
)

# 자막 스타일 기본값 — 1080p 기준 가독성 (맑은 고딕 볼드 + 두꺼운 외곽선)
# 넷플릭스류: 크고 굵게, 화면 아래 여백 충분히, 한 번에 1~2줄만.
DEFAULT_SUBTITLE_STYLE = {
    "FontName": "Malgun Gothic",
    "Fontsize": "20",
    "Bold": "1",
    "PrimaryColour": "&H00FFFFFF",
    "OutlineColour": "&HC0000000",
    "BackColour": "&H00000000",
    "BorderStyle": "1",
    "Outline": "2.2",
    "Shadow": "1.0",
    "MarginV": "58",
    "MarginL": "100",
    "MarginR": "100",
    "WrapStyle": "2",
}

_TIME_RE = re.compile(
    r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})"
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class VideoComposer:
    def __init__(
        self,
        logger: ADOSLogger | None = None,
        ffmpeg: str = "ffmpeg",
        ffprobe: str = "ffprobe",
    ):
        self.logger = logger
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe

    # --- 공통 실행 헬퍼 ---
    def _run(self, cmd: list[str], cwd: str | Path | None = None) -> subprocess.CompletedProcess:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise ADOSEngineError(
                f"명령 실행 실패 (exit={result.returncode}): {cmd[0]}",
                location="VideoComposer._run",
                cause=(result.stderr or "")[-2000:],
                suggested_fix="ffmpeg 설치와 입력 파일 경로를 확인하세요.",
            )
        return result

    def probe_duration(self, media_path: str | Path) -> float:
        media_path = Path(media_path)
        if not media_path.is_file():
            raise ADOSFileNotFoundError(
                f"미디어 파일이 없습니다: {media_path}",
                location="VideoComposer.probe_duration",
                suggested_fix="파일 경로를 확인하세요.",
            )
        result = self._run(
            [
                self.ffprobe, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(media_path),
            ]
        )
        return float(result.stdout.strip())

    # --- SRT 파싱/검증 ---
    def parse_srt(self, srt_path: str | Path) -> list[dict]:
        """SRT 파일을 큐 목록으로 파싱한다 (BOM/CRLF 허용)."""
        srt_path = Path(srt_path)
        if not srt_path.is_file():
            raise ADOSFileNotFoundError(
                f"자막 파일이 없습니다: {srt_path}",
                location="VideoComposer.parse_srt",
                suggested_fix="subtitles/subtitles_{lang}.srt 경로를 확인하세요.",
            )
        text = srt_path.read_text(encoding="utf-8-sig")
        cues = []
        for block in re.split(r"\n\s*\n", text.strip()):
            lines = [line.strip("\r") for line in block.strip().splitlines()]
            if not lines:
                continue
            match = None
            time_line_index = None
            for i, line in enumerate(lines[:2]):
                match = _TIME_RE.search(line)
                if match:
                    time_line_index = i
                    break
            if not match:
                continue
            h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(g) for g in match.groups())
            start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
            end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000
            cue_text = "\n".join(lines[time_line_index + 1:]).strip()
            cues.append(
                {
                    "index": len(cues) + 1,
                    "start_seconds": start,
                    "end_seconds": end,
                    "text": cue_text,
                }
            )
        return cues

    def validate_subtitles(
        self, srt_path: str | Path, video_duration_seconds: float | None = None
    ) -> dict:
        """SRT 내용을 검증한다 — 큐 존재, 시간 순서, 겹침, 영상 길이 커버리지."""
        cues = self.parse_srt(srt_path)
        issues = []
        if not cues:
            issues.append("no_cues")
        for cue in cues:
            if cue["end_seconds"] <= cue["start_seconds"]:
                issues.append(f"cue_{cue['index']}_non_positive_duration")
            if not cue["text"]:
                issues.append(f"cue_{cue['index']}_empty_text")
        for prev, cur in zip(cues, cues[1:]):
            if cur["start_seconds"] < prev["end_seconds"]:
                issues.append(f"cue_{cur['index']}_overlaps_previous")
        coverage_ratio = None
        if video_duration_seconds and cues:
            last_end = max(cue["end_seconds"] for cue in cues)
            coverage_ratio = round(last_end / video_duration_seconds, 4)
            if last_end > video_duration_seconds + 0.5:
                issues.append("last_cue_exceeds_video_duration")
            if coverage_ratio < 0.5:
                issues.append("subtitles_cover_less_than_half_of_video")
        report = {
            "srt_path": str(srt_path),
            "cue_count": len(cues),
            "first_cue_start": cues[0]["start_seconds"] if cues else None,
            "last_cue_end": cues[-1]["end_seconds"] if cues else None,
            "coverage_ratio": coverage_ratio,
            "issues": issues,
            "status": "PASS" if not issues else "FAIL",
            "created_at": _now_iso(),
        }
        return report

    # --- 세그먼트 concat + 나레이션 mux ---
    def concat_from_lists(
        self,
        build_dir: str | Path,
        output_path: str | Path,
        video_list: str = "video_list.txt",
        narration: str = "narration.wav",
        audio_list: str = "audio_list.txt",
    ) -> Path:
        """빌드 폴더의 concat 리스트로 무자막 베이스 영상을 만든다.

        narration.wav가 있으면 그대로 쓰고, 없으면 audio_list를 concat해 만든다.
        리스트 파일 안의 상대 경로가 유지되도록 cwd를 build_dir로 고정한다.
        cwd가 바뀌므로 리스트 밖의 경로는 전부 절대 경로로 변환해 넘긴다.
        """
        build_dir = Path(build_dir).resolve()
        output_path = Path(output_path).resolve()
        if not (build_dir / video_list).is_file():
            raise ADOSFileNotFoundError(
                f"{video_list}가 없습니다: {build_dir / video_list}",
                location="VideoComposer.concat_from_lists",
                suggested_fix="세그먼트 빌드 폴더(video_list.txt 포함)를 지정하세요.",
            )
        narration_path = build_dir / narration
        if not narration_path.is_file():
            if not (build_dir / audio_list).is_file():
                raise ADOSFileNotFoundError(
                    f"{narration}도 {audio_list}도 없습니다: {build_dir}",
                    location="VideoComposer.concat_from_lists",
                    suggested_fix="나레이션 wav 또는 audio_list.txt를 준비하세요.",
                )
            narration_path = build_dir / "_ados_narration_concat.wav"
            # -c copy 금지: 세그먼트 간 샘플레이트/채널이 다르면 exit 0인 채로
            # 손상된 wav가 나온다. PCM 재인코딩으로 파라미터를 통일한다.
            self._run(
                [
                    self.ffmpeg, "-y", "-f", "concat", "-safe", "0",
                    "-i", audio_list, "-c:a", "pcm_s16le", narration_path.name,
                ],
                cwd=build_dir,
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._run(
            [
                self.ffmpeg, "-y",
                "-f", "concat", "-safe", "0", "-i", video_list,
                "-i", str(narration_path),
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(output_path),
            ],
            cwd=build_dir,
        )
        if self.logger:
            self.logger.info(
                f"베이스 영상 합성 완료: {output_path.name}",
                metadata={"output": str(output_path)},
            )
        return output_path

    # --- BGM 믹싱 (사이드체인 덕킹) ---
    def mix_bgm(
        self,
        video_path: str | Path,
        bgm_path: str | Path,
        output_path: str | Path,
        music_gain_db: float = -20.0,
        duck_gain_db: float = -32.0,
        fade_in_seconds: float = 2.0,
        fade_out_seconds: float = 2.5,
    ) -> Path:
        """영상의 나레이션 위에 BGM을 깐다 — 나레이션 구간은 자동 덕킹.

        나레이션(영상의 오디오)을 사이드체인 신호로 써서, 나레이션이
        나올 때 BGM 음량을 duck_gain_db까지 내린다. BGM은 영상 길이에
        맞춰 자동 루프하고 시작/끝 페이드를 넣는다. 영상 스트림은 재인코딩
        하지 않는다(-c:v copy).
        """
        video_path = Path(video_path).resolve()
        bgm_path = Path(bgm_path).resolve()
        output_path = Path(output_path).resolve()
        for path, name in ((video_path, "영상"), (bgm_path, "BGM")):
            if not path.is_file():
                raise ADOSFileNotFoundError(
                    f"{name} 파일이 없습니다: {path}",
                    location="VideoComposer.mix_bgm",
                    suggested_fix="입력 경로를 확인하세요.",
                )
        duration = self.probe_duration(video_path)
        # 나레이션이 나오는 구간에서 BGM을 누른다 (사이드체인 컴프레션).
        # ratio가 클수록 더 깊이 눌린다. 목표 덕킹 깊이(music-duck)에서
        # ratio를 근사한다 — release를 길게 잡아 말소리 사이에서 펌핑 방지.
        duck_delta = max(3.0, music_gain_db - duck_gain_db)
        ratio = min(20.0, max(2.0, duck_delta / 2.0))
        filter_complex = (
            f"[1:a]volume={music_gain_db}dB,aloop=loop=-1:size=2e9,"
            f"atrim=0:{duration:.3f},"
            f"afade=t=in:st=0:d={fade_in_seconds},"
            f"afade=t=out:st={max(0.0, duration - fade_out_seconds):.3f}:d={fade_out_seconds}[bgm];"
            f"[0:a]asplit=2[nar][sc];"
            f"[bgm][sc]sidechaincompress=threshold=0.02:ratio={ratio:.1f}:"
            f"attack=20:release=500[ducked];"
            f"[nar][ducked]amix=inputs=2:duration=first:dropout_transition=0:"
            f"weights=1 1:normalize=0[aout]"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._run(
            [
                self.ffmpeg, "-y",
                "-i", str(video_path),
                "-i", str(bgm_path),
                "-filter_complex", filter_complex,
                "-map", "0:v:0", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                str(output_path),
            ]
        )
        if self.logger:
            self.logger.info(
                f"BGM 믹싱 완료: {output_path.name}",
                metadata={"output": str(output_path), "bgm": bgm_path.name},
            )
        return output_path

    # --- 자막 번인 ---
    @staticmethod
    def _style_string(style: dict) -> str:
        return ",".join(f"{key}={value}" for key, value in style.items())

    def _subtitles_filter(self, srt_filename: str, style: dict) -> str:
        return f"subtitles={srt_filename}:force_style='{self._style_string(style)}'"

    def burn_subtitles(
        self,
        video_path: str | Path,
        srt_path: str | Path,
        output_path: str | Path,
        style: dict | None = None,
    ) -> Path:
        """자막을 영상에 굽는다(burn-in).

        Windows 한글 경로 함정 회피: subtitles 필터 인자는 파일명만 쓰고,
        ffmpeg의 cwd를 srt가 있는 폴더로 고정한다 (드라이브 콜론/한글
        이스케이프 문제를 원천 차단).
        """
        video_path = Path(video_path).resolve()
        srt_path = Path(srt_path).resolve()
        output_path = Path(output_path).resolve()
        for path, name in ((video_path, "영상"), (srt_path, "자막")):
            if not path.is_file():
                raise ADOSFileNotFoundError(
                    f"{name} 파일이 없습니다: {path}",
                    location="VideoComposer.burn_subtitles",
                    suggested_fix="입력 경로를 확인하세요.",
                )
        cues = self.parse_srt(srt_path)
        if not cues:
            raise ADOSValidationError(
                f"자막 큐가 없습니다: {srt_path}",
                location="VideoComposer.burn_subtitles",
                suggested_fix="SRT 내용을 확인하세요.",
            )
        merged_style = dict(DEFAULT_SUBTITLE_STYLE)
        if style:
            merged_style.update(style)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._run(
            [
                self.ffmpeg, "-y",
                "-i", str(video_path),
                "-vf", self._subtitles_filter(srt_path.name, merged_style),
                "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-pix_fmt", "yuv420p",
                "-c:a", "copy",
                str(output_path),
            ],
            cwd=srt_path.parent,
        )
        if self.logger:
            self.logger.info(
                f"자막 번인 완료: {output_path.name} ({len(cues)}큐)",
                metadata={"output": str(output_path), "cue_count": len(cues)},
            )
        return output_path

    def burn_subtitles_from_cues(
        self,
        video_path: str | Path,
        cues: list[dict],
        style: dict,
        output_path: str | Path,
        ass_name: str = "_ados_subtitles.ass",
    ) -> Path:
        """리플로우된 큐 + 해석된 스타일로 ASS를 만들어 영상에 굽는다.

        SRT + force_style 대신 .ass를 직접 생성한다. 이유: subtitles 필터가 SRT를
        ASS로 변환할 때 기본 해상도(384x288)로 스케일해 폰트가 뻥튀기되고 줄바꿈이
        통제되지 않던 문제를, PlayRes(1920x1080)를 명시한 .ass로 원천 차단한다.
        한글 경로 함정 회피: .ass는 output 폴더에 쓰고 파일명만 필터에 넘긴다.
        """
        from engines.composition.subtitle_style import build_ass

        video_path = Path(video_path).resolve()
        output_path = Path(output_path).resolve()
        if not video_path.is_file():
            raise ADOSFileNotFoundError(
                f"영상 파일이 없습니다: {video_path}",
                location="VideoComposer.burn_subtitles_from_cues",
                suggested_fix="입력 경로를 확인하세요.",
            )
        if not cues:
            raise ADOSValidationError(
                "자막 큐가 비어 있습니다.",
                location="VideoComposer.burn_subtitles_from_cues",
                suggested_fix="reflow_cues 결과를 확인하세요.",
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        ass_path = output_path.parent / ass_name
        # Aegisub 관례대로 UTF-8 BOM으로 저장 — libass가 인코딩을 안전하게 감지.
        ass_path.write_text(build_ass(cues, style), encoding="utf-8-sig")
        self._run(
            [
                self.ffmpeg, "-y",
                "-i", str(video_path),
                "-vf", f"subtitles={ass_name}",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-pix_fmt", "yuv420p",
                "-c:a", "copy",
                str(output_path),
            ],
            cwd=ass_path.parent,
        )
        if self.logger:
            self.logger.info(
                f"ASS 자막 번인 완료: {output_path.name} ({len(cues)}큐)",
                metadata={"output": str(output_path), "cue_count": len(cues)},
            )
        return output_path

    # --- 번인 검증 ---
    # 번인 전/후 같은 시각 프레임의 하단 밴드 차이가 이 값 이상이면 자막 픽셀로 판정.
    # 재인코딩 노이즈(crf 18)는 보통 YMAX 20 이하, 자막 글자/외곽선은 100 이상이다.
    SUBTITLE_DIFF_THRESHOLD = 48.0

    def _bottom_band_diff(
        self, base_video: Path, subtitled_video: Path, at_seconds: float
    ) -> float:
        """같은 시각의 번인 전/후 프레임에서 하단 25% 밴드 차이(YMAX)를 잰다.

        밝기 절대값 휴리스틱은 밝은 장면(하늘/흰 배경)에서 자막이 없어도
        통과하는 오탐이 있어, 프레임 차분(difference) 방식을 쓴다 —
        자막은 검은 외곽선을 포함하므로 어떤 배경에서도 큰 차이를 만든다.
        """
        band = "crop=iw:ih/4:0:3*ih/4"
        result = self._run(
            [
                self.ffmpeg, "-hide_banner",
                "-ss", f"{at_seconds:.3f}", "-i", str(base_video),
                "-ss", f"{at_seconds:.3f}", "-i", str(subtitled_video),
                "-filter_complex",
                f"[0:v]{band}[a];[1:v]{band}[b];"
                "[a][b]blend=all_mode=difference,signalstats,metadata=print:file=-",
                "-frames:v", "1",
                "-f", "null", "-",
            ]
        )
        for line in result.stdout.splitlines():
            marker = "lavfi.signalstats.YMAX="
            if marker in line:
                return float(line.split(marker)[1].strip())
        raise ADOSEngineError(
            f"signalstats 출력을 파싱하지 못했습니다: {subtitled_video} @ {at_seconds:.3f}s",
            location="VideoComposer._bottom_band_diff",
            suggested_fix="ffmpeg 버전(blend/signalstats/metadata 필터 지원)을 확인하세요.",
        )

    def verify_burned_subtitles(
        self,
        base_video: str | Path,
        subtitled_video: str | Path,
        srt_path: str | Path,
        sample_cues: int = 3,
    ) -> dict:
        """자막이 실제로 화면에 렌더링됐는지 검증한다.

        번인 전(base) 영상과 번인 후 영상의 같은 프레임을 비교해,
        자막 큐 중간 시점의 하단 밴드에 유의미한 픽셀 차이가 있어야 한다.
        """
        base_video = Path(base_video)
        subtitled_video = Path(subtitled_video)
        cues = self.parse_srt(srt_path)
        if not cues:
            raise ADOSValidationError(
                f"자막 큐가 없습니다: {srt_path}",
                location="VideoComposer.verify_burned_subtitles",
                suggested_fix="SRT 내용을 확인하세요.",
            )
        duration = self.probe_duration(subtitled_video)

        step = max(1, len(cues) // sample_cues)
        sampled = cues[::step][:sample_cues]
        checks = []
        for cue in sampled:
            midpoint = min((cue["start_seconds"] + cue["end_seconds"]) / 2, duration - 0.1)
            diff_ymax = self._bottom_band_diff(base_video, subtitled_video, midpoint)
            checks.append(
                {
                    "cue_index": cue["index"],
                    "at_seconds": round(midpoint, 3),
                    "diff_ymax": diff_ymax,
                    "subtitle_pixels_detected": diff_ymax >= self.SUBTITLE_DIFF_THRESHOLD,
                }
            )
        all_detected = all(check["subtitle_pixels_detected"] for check in checks)
        report = {
            "base_video": str(base_video),
            "subtitled_video": str(subtitled_video),
            "srt_path": str(srt_path),
            "video_duration_seconds": round(duration, 3),
            "cue_count": len(cues),
            "sampled_checks": checks,
            "subtitles_visible": all_detected,
            "status": "PASS" if all_detected else "FAIL",
            "created_at": _now_iso(),
        }
        if self.logger:
            self.logger.info(
                f"자막 번인 검증: {report['status']}",
                metadata={"video": str(subtitled_video), "status": report["status"]},
            )
        return report
