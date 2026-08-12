# -*- coding: utf-8 -*-
"""최종 영상 합성 — 세그먼트 concat + 나레이션 mux + BGM 믹싱 + 자막 번인 + 검증.

수동 워크스페이스의 빌드 세그먼트와 자막(srt)으로 자막이 실제로 보이는
최종 영상을 만든다. bgm_library/의 음원이 있으면 자동 덕킹 믹싱한다.
업로드·외부 API 호출은 없다 (docs/36).

실행: 프로젝트 루트에서
  python scripts/compose_final_video.py {workspace_dir} [build_subdir] [lang] [--bgm 파일명]
  예) python scripts/compose_final_video.py manual_assets/20260710-141033-future-million-year-human notes/build3min ko
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import load_yaml  # noqa: E402
from engines.composition import VideoComposer  # noqa: E402

USAGE = """사용법: python scripts/compose_final_video.py {workspace_dir} [build_subdir] [lang] [--bgm 파일명]

  workspace_dir: 수동 자산 워크스페이스 경로
    예) manual_assets/20260710-141033-future-million-year-human
  build_subdir : 세그먼트 빌드 폴더 (기본: notes/build3min)
                 video_list.txt와 narration.wav(또는 audio_list.txt)가 있어야 한다.
                 빌드 폴더가 없으면 video/final_video.mp4를 베이스로 사용한다.
  lang         : 번인할 자막 언어 (기본: ko) — subtitles/subtitles_{lang}.srt
  --bgm 파일명 : bgm_library/의 특정 트랙 사용 (기본: config 기본 트랙, 없으면 BGM 생략)"""


def resolve_bgm(bgm_arg: str | None) -> Path | None:
    """BGM 트랙을 찾는다. 없으면 None (BGM 없이 진행)."""
    bgm_dir = PROJECT_ROOT / "bgm_library"
    if bgm_arg:
        candidate = bgm_dir / bgm_arg
        return candidate if candidate.is_file() else None
    config_path = PROJECT_ROOT / "config" / "bgm_library.yaml"
    if config_path.is_file():
        config = load_yaml(config_path)
        default = (config or {}).get("default_track")
        if default and (bgm_dir / default).is_file():
            return bgm_dir / default
    return None


def bgm_mix_params() -> dict:
    config_path = PROJECT_ROOT / "config" / "bgm_library.yaml"
    defaults = {
        "music_gain_db": -20.0, "duck_gain_db": -32.0,
        "fade_in_seconds": 2.0, "fade_out_seconds": 2.5,
    }
    if config_path.is_file():
        config = load_yaml(config_path) or {}
        mix = config.get("mix") or {}
        for key in defaults:
            if key in mix:
                defaults[key] = mix[key]
    return defaults


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(USAGE)
        return 1
    bgm_arg = None
    if "--bgm" in argv:
        idx = argv.index("--bgm")
        bgm_arg = argv[idx + 1] if idx + 1 < len(argv) else None
        argv = argv[:idx] + argv[idx + 2:]
    workspace = Path(argv[0])
    build_subdir = argv[1] if len(argv) > 1 else "notes/build3min"
    lang = argv[2] if len(argv) > 2 else "ko"

    srt_path = workspace / "subtitles" / f"subtitles_{lang}.srt"
    if not srt_path.is_file():
        print(f"자막 파일이 없습니다: {srt_path}")
        print()
        print(USAGE)
        return 1

    composer = VideoComposer()
    build_dir = workspace / build_subdir

    # 1. 베이스 영상 확보 (무자막, 나레이션만)
    if (build_dir / "video_list.txt").is_file():
        base_path = workspace / "video" / "final_video_base.mp4"
        composer.concat_from_lists(build_dir, base_path)
        base_source = f"세그먼트 재조립 ({build_subdir})"
    else:
        base_path = workspace / "video" / "final_video.mp4"
        base_source = "기존 video/final_video.mp4"
        if not base_path.is_file():
            print(f"베이스 영상이 없습니다: {base_path}")
            print()
            print(USAGE)
            return 1

    base_duration = composer.probe_duration(base_path)

    # 2. BGM 믹싱 (음원이 있으면 — 나레이션 구간 자동 덕킹)
    bgm_path = resolve_bgm(bgm_arg)
    if bgm_path:
        mixed_path = workspace / "video" / "final_video_bgm.mp4"
        composer.mix_bgm(base_path, bgm_path, mixed_path, **bgm_mix_params())
        base_path = mixed_path
        bgm_status = bgm_path.name
    else:
        bgm_status = "없음 (bgm_library/에 음원을 넣으면 자동 믹싱)"

    # 3. SRT 내용 검증
    srt_report = composer.validate_subtitles(srt_path, video_duration_seconds=base_duration)
    if srt_report["status"] != "PASS":
        print(f"자막 검증 실패: {srt_report['issues']}")
        return 1

    # 4. 자막 번인
    output_path = workspace / "video" / f"final_video_subtitled_{lang}.mp4"
    composer.burn_subtitles(base_path, srt_path, output_path)

    # 5. 검증 — 길이 + 자막 가시성 (번인 전/후 프레임 차분)
    output_duration = composer.probe_duration(output_path)
    duration_ok = abs(output_duration - base_duration) <= 0.2
    burn_report = composer.verify_burned_subtitles(base_path, output_path, srt_path)

    passed = duration_ok and burn_report["subtitles_visible"]
    print(f"workspace           : {workspace}")
    print(f"base_source         : {base_source}")
    print(f"bgm                 : {bgm_status}")
    print(f"base_video          : {base_path}")
    print(f"base_duration       : {base_duration:.3f}s")
    print(f"srt                 : {srt_path} ({srt_report['cue_count']}큐, coverage {srt_report['coverage_ratio']})")
    print(f"subtitled_video     : {output_path}")
    print(f"subtitled_duration  : {output_duration:.3f}s (일치: {duration_ok})")
    print(f"subtitles_visible   : {burn_report['subtitles_visible']}")
    for check in burn_report["sampled_checks"]:
        print(
            f"  - cue {check['cue_index']:>2} @ {check['at_seconds']:>8.3f}s"
            f"  diff_YMAX={check['diff_ymax']:<6.1f} 감지={check['subtitle_pixels_detected']}"
        )
    print(f"result              : {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
