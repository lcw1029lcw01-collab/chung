# -*- coding: utf-8 -*-
"""Longform composition — 롱폼 영상 합성 공통 실행기.

검증된 수동 빌드 스크립트(블록별 나레이션 타이밍 분배 + 켄번즈/모션 세그먼트 +
블록 자막 큐) 방식을 에피소드 전용 절대 경로·채널명 없이 일반화했다.

입력: project_path + production manifest(블록별 오디오/컷) + 채널 브랜드 프로필
동작:
  1. 모든 자산 존재 검사 (상대 경로만, 프로젝트 루트 탈출 금지)
  2. ffprobe로 실제 오디오 길이 측정
  3. 블록별 나레이션 시간을 컷 개수로 분배 (image → Ken Burns, motion → 슬로우 맞춤)
  4. video/audio concat (VideoComposer 재사용)
  5. 채널 자막 preset 해석 → 블록 큐 리플로우 → ASS 생성·번인
  6. 길이·오디오 스트림·자막 가시성 검증
ffmpeg 실행은 전부 VideoComposer를 통해서만 한다 (로직 복사 금지).
기존 출력 파일은 force 없이 덮어쓰지 않는다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSValidationError,
)

from .subtitle_reflow import char_width, reading_speed_warnings, reflow_cues
from .subtitle_style import resolve_style
from .video_composer import VideoComposer

# Ken Burns 모션 프리셋 (검증된 수동 빌드와 동일 파라미터)
_PRESCALE = "scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,setsar=1"
_MOTIONS = {
    "zi": "zoompan=z='1+0.08*on/{d}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={d}:s=1920x1080:fps={fps}",
    "zo": "zoompan=z='1.08-0.08*on/{d}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={d}:s=1920x1080:fps={fps}",
    "pl": "zoompan=z='1.06':x='(iw-iw/zoom)*on/{d}':y='(ih-ih/zoom)/2':d={d}:s=1920x1080:fps={fps}",
    "pr": "zoompan=z='1.06':x='(iw-iw/zoom)*(1-on/{d})':y='(ih-ih/zoom)/2':d={d}:s=1920x1080:fps={fps}",
}
_KB_ROTATION = ["zi", "pl", "pr", "zo"]
_ENCODE_ARGS = [
    "-c:v", "libx264", "-crf", "18", "-preset", "medium",
    "-pix_fmt", "yuv420p", "-an",
]

MANIFEST_REQUIRED_FIELDS = ["blocks"]
BLOCK_REQUIRED_FIELDS = ["id", "text", "audio", "cuts"]

DEFAULT_FPS = 25
DEFAULT_SILENCE = 0.45
DEFAULT_TAIL = 1.2
_MIN_FRAMES = 28


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LongformCompositionExecutor:
    def __init__(self, composer: VideoComposer | None = None, logger: ADOSLogger | None = None):
        self.composer = composer or VideoComposer()
        self.logger = logger

    # --- 경로 안전 ---
    @staticmethod
    def _safe_join(base: Path, relative: str, what: str) -> Path:
        rel = Path(str(relative))
        if rel.is_absolute() or str(relative).startswith(("\\", "/")):
            raise ADOSValidationError(
                f"{what} 경로는 상대 경로여야 합니다: {relative}",
                location="LongformCompositionExecutor._safe_join",
                suggested_fix="프로젝트 루트 기준 상대 경로를 사용하세요.",
            )
        resolved = (base / rel).resolve()
        base_resolved = base.resolve()
        if resolved != base_resolved and base_resolved not in resolved.parents:
            raise ADOSValidationError(
                f"{what} 경로가 프로젝트 루트를 벗어납니다: {relative}",
                location="LongformCompositionExecutor._safe_join",
                suggested_fix="'..' 등 루트 탈출 요소를 제거하세요.",
            )
        return resolved

    # --- manifest 검증 ---
    def validate_manifest(self, project_path: str | Path, manifest: dict) -> dict:
        """manifest 구조와 모든 자산 존재를 검사한다. 누락 목록이 있으면 에러."""
        project_path = Path(project_path)
        for f in MANIFEST_REQUIRED_FIELDS:
            if f not in manifest:
                raise ADOSValidationError(
                    f"production manifest 필수 필드 누락: {f}",
                    location="LongformCompositionExecutor.validate_manifest",
                )
        assets_root = self._safe_join(
            project_path, manifest.get("assets_root", "assets/production"), "assets_root"
        )
        missing: list[str] = []
        resolved_blocks = []
        for block in manifest["blocks"]:
            for f in BLOCK_REQUIRED_FIELDS:
                if f not in block:
                    raise ADOSValidationError(
                        f"block 필수 필드 누락: {f} (block={block.get('id', '?')})",
                        location="LongformCompositionExecutor.validate_manifest",
                    )
            audio = self._safe_join(assets_root, block["audio"], f"block {block['id']} audio")
            if not audio.is_file():
                missing.append(str(Path(block["audio"])))
            cuts = []
            if not block["cuts"]:
                raise ADOSValidationError(
                    f"block {block['id']}: cuts가 비어 있습니다",
                    location="LongformCompositionExecutor.validate_manifest",
                )
            for cut in block["cuts"]:
                source_key = "motion" if cut.get("motion") else "image"
                source_rel = cut.get(source_key)
                if not cut.get("id") or not source_rel:
                    raise ADOSValidationError(
                        f"cut에 id와 image/motion 중 하나가 필요합니다: {cut}",
                        location="LongformCompositionExecutor.validate_manifest",
                    )
                source = self._safe_join(assets_root, source_rel, f"cut {cut['id']}")
                if not source.is_file():
                    missing.append(str(Path(source_rel)))
                cuts.append({"id": cut["id"], "kind": source_key, "path": source,
                             "kb": cut.get("kb")})
            resolved_blocks.append({"id": block["id"], "text": block["text"],
                                    "audio": audio, "cuts": cuts})
        if missing:
            raise ADOSFileNotFoundError(
                f"누락 자산 {len(missing)}건: {', '.join(missing[:10])}"
                + (" ..." if len(missing) > 10 else ""),
                location="LongformCompositionExecutor.validate_manifest",
                suggested_fix="assets_root 아래에 누락된 파일을 배치한 뒤 재실행하세요.",
            )
        return {"assets_root": assets_root, "blocks": resolved_blocks}

    # --- 세그먼트 빌드 ---
    def _build_segment(self, cut: dict, frames: int, fps: int, build_dir: Path) -> str:
        seg_name = f"seg_{cut['id']}.mp4"
        seg_path = build_dir / seg_name
        if cut["kind"] == "motion":
            source_duration = self.composer.probe_duration(cut["path"])
            factor = max(1.0, (frames / fps) / max(source_duration, 0.01))
            self.composer._run([
                self.composer.ffmpeg, "-y", "-i", str(cut["path"]),
                "-vf",
                f"setpts=PTS*{factor:.4f},fps={fps},"
                "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
                "crop=1920:1080,setsar=1",
                "-frames:v", str(frames), *_ENCODE_ARGS, str(seg_path),
            ])
        else:
            motion = _MOTIONS[cut["kb"] or _KB_ROTATION[self._kb_index % 4]]
            self._kb_index += 1
            self.composer._run([
                self.composer.ffmpeg, "-y", "-i", str(cut["path"]),
                "-vf", f"{_PRESCALE},{motion.format(d=frames, fps=fps)}",
                "-frames:v", str(frames), *_ENCODE_ARGS, str(seg_path),
            ])
        return seg_name

    def _make_silence(self, path: Path, seconds: float) -> None:
        self.composer._run([
            self.composer.ffmpeg, "-y", "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=mono:d={seconds}",
            "-c:a", "pcm_s16le", str(path),
        ])

    # --- 메인 합성 ---
    def compose(
        self,
        project_path: str | Path,
        manifest: dict,
        brand_profile: dict,
        subtitle_styles: dict,
        output_rel: str = "assets/video/final_video_subtitled.mp4",
        build_rel: str = "assets/video/build",
        force: bool = False,
        verify: bool = True,
        quality_rules: dict | None = None,
    ) -> dict:
        project_path = Path(project_path)
        output_path = self._safe_join(project_path, output_rel, "output")
        if output_path.is_file() and not force:
            raise ADOSValidationError(
                f"출력 파일이 이미 존재합니다 (--force 없이 덮어쓰지 않음): {output_rel}",
                location="LongformCompositionExecutor.compose",
                suggested_fix="--force로 재실행하거나 다른 출력 경로를 지정하세요.",
            )

        resolved = self.validate_manifest(project_path, manifest)
        fps = int(manifest.get("fps", DEFAULT_FPS))
        silence = float(manifest.get("inter_block_silence_seconds", DEFAULT_SILENCE))
        tail = float(manifest.get("tail_seconds", DEFAULT_TAIL))

        build_dir = self._safe_join(project_path, build_rel, "build_dir")
        build_dir.mkdir(parents=True, exist_ok=True)
        self._kb_index = 0

        # 1. 블록 오디오 실측 + 세그먼트 생성 + 블록 자막 큐
        durations = {b["id"]: self.composer.probe_duration(b["audio"]) for b in resolved["blocks"]}
        segment_lines: list[str] = []
        audio_lines: list[str] = []
        block_cues: list[dict] = []
        audio_cursor = 0.0
        blocks = resolved["blocks"]
        self._make_silence(build_dir / "_sil.wav", silence)
        self._make_silence(build_dir / "_tail.wav", tail)
        for bi, block in enumerate(blocks):
            is_last = bi == len(blocks) - 1
            cuts = block["cuts"]
            base_share = durations[block["id"]] / len(cuts)
            for ci, cut in enumerate(cuts):
                extra = (tail if is_last else silence) if ci == len(cuts) - 1 else 0.0
                frames = max(_MIN_FRAMES, round((base_share + extra) * fps))
                segment_lines.append(f"file '{self._build_segment(cut, frames, fps, build_dir)}'")
            block_cues.append({
                "index": len(block_cues) + 1,
                "start_seconds": audio_cursor,
                "end_seconds": audio_cursor + durations[block["id"]],
                "text": block["text"],
            })
            audio_lines.append(f"file '{block['audio'].as_posix()}'")
            audio_lines.append(
                f"file '{(build_dir / ('_tail.wav' if is_last else '_sil.wav')).as_posix()}'"
            )
            audio_cursor += durations[block["id"]] + (tail if is_last else silence)

        (build_dir / "video_list.txt").write_text("\n".join(segment_lines) + "\n", encoding="utf-8")
        (build_dir / "audio_list.txt").write_text("\n".join(audio_lines) + "\n", encoding="utf-8")

        # 2. concat + 나레이션 mux (VideoComposer 재사용)
        base_path = build_dir / "_base_nosub.mp4"
        self.composer.concat_from_lists(build_dir, base_path)
        base_duration = self.composer.probe_duration(base_path)

        # 3. 채널 자막 preset 해석 + 리플로우
        preset_name = brand_profile.get("subtitle_style", "documentary")
        style = resolve_style(
            subtitle_styles, preset_name, brand_profile.get("subtitle_overrides")
        )
        max_chars = style.get("max_chars_per_line", 16)
        display_cues = reflow_cues(
            block_cues, max_chars_per_line=max_chars, max_lines=style.get("max_lines", 2)
        )
        overflow = [
            c for c in display_cues
            if any(char_width(line) > max_chars for line in c.get("lines", []))
        ]
        speed_warnings = reading_speed_warnings(
            display_cues, max_cps=(quality_rules or {}).get("gate", {}).get("subtitle_max_cps", 12)
        )

        # 4. ASS 번인
        self.composer.burn_subtitles_from_cues(base_path, display_cues, style, output_path)
        output_duration = self.composer.probe_duration(output_path)
        duration_ok = abs(output_duration - base_duration) <= 0.2

        # 5. 검증 — 자막 가시성 (표시 큐 임시 SRT)
        burn_report = None
        if verify:
            srt_path = build_dir / "_display_cues.srt"
            srt_path.write_text(self._cues_to_srt(display_cues), encoding="utf-8")
            burn_report = self.composer.verify_burned_subtitles(
                base_path, output_path, srt_path, sample_cues=6
            )

        report = {
            "output_rel": str(output_rel).replace("\\", "/"),
            "base_duration_seconds": round(base_duration, 3),
            "output_duration_seconds": round(output_duration, 3),
            "duration_match": duration_ok,
            "fps": fps,
            "block_count": len(blocks),
            "segment_count": len(segment_lines),
            "block_cue_count": len(block_cues),
            "display_cue_count": len(display_cues),
            "line_overflow_count": len(overflow),
            "reading_speed_warning_count": len(speed_warnings),
            "subtitle_preset": preset_name,
            "subtitles_visible": burn_report["subtitles_visible"] if burn_report else None,
            "verified": bool(burn_report),
            "status": "PASS" if duration_ok and (not burn_report or burn_report["subtitles_visible"]) else "FAIL",
            "created_at": _now_iso(),
        }
        if self.logger:
            self.logger.info(
                f"롱폼 합성 완료: {report['status']} ({output_duration:.1f}s)",
                metadata={"output": str(output_path), "status": report["status"]},
            )
        return report

    @staticmethod
    def _cues_to_srt(cues: list[dict]) -> str:
        def ts(seconds: float) -> str:
            ms = int(round(seconds * 1000))
            hours, ms = divmod(ms, 3600000)
            minutes, ms = divmod(ms, 60000)
            secs, ms = divmod(ms, 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

        parts = []
        for i, cue in enumerate(cues, 1):
            text = "\n".join(cue.get("lines") or [cue.get("text", "")])
            parts.append(f"{i}\n{ts(cue['start_seconds'])} --> {ts(cue['end_seconds'])}\n{text}\n")
        return "\n".join(parts)
