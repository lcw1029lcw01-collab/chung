# -*- coding: utf-8 -*-
"""품질 게이트 — 최종 영상을 100점 만점으로 채점한다 (95점 이상 PASS).

근거: docs/26_QUALITY_ENGINE.md (95점 이상 PASS) + docs/36 검증.
합성된 영상 + 워크스페이스를 실제로 검사한다. 사람이 눈으로 확인해야 하는
항목(글리프 깨짐 등)은 사람 검토로 남기고, 자동 검증 가능한 것만 채점한다.

실행: 프로젝트 루트에서
  python scripts/quality_gate.py {workspace} [build_subdir] [lang] [--langs en,ja|none]
"""
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from engines.composition import VideoComposer  # noqa: E402
from engines.composition.subtitle_translation import validate_translated_srt  # noqa: E402

# 채점 항목 (합 100) — 각 항목: (이름, 배점)
# 주의: 켄번즈(이미지+카메라무빙)는 폴백이 아니라 정식 기법이다 (docs/38 —
# 이미지+무빙 50~60%가 목표). 따라서 "영상 100%"가 아니라 "자산 커버리지"와
# "자산 믹스 적정성(영상이 임팩트 구간에 15~40%)"으로 채점한다.
RUBRIC = [
    ("자막 가시성 (실제 프레임에 자막 렌더)", 20),
    ("길이 정합 (영상=나레이션, ±0.3s)", 15),
    ("해상도 (1920x1080)", 10),
    ("장면 전환 밀도 (평균 샷 ≤ 9초)", 15),
    ("자산 커버리지 (모든 샷에 MJ 자산)", 10),
    ("자산 믹스 적정성 (영상 15~40%)", 5),
    ("나레이션 오디오 존재", 10),
    ("no-text 안전 (프롬프트 negative 포함)", 15),
]
PASS_SCORE = 95


def probe(path, entries):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", entries,
         "-of", "json", str(path)], capture_output=True, text=True)
    return json.loads(out.stdout or "{}")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    langs_value = "en,ja"
    if "--langs" in argv:
        idx = argv.index("--langs")
        langs_value = argv[idx + 1] if idx + 1 < len(argv) else "none"
        argv = argv[:idx] + argv[idx + 2:]
    target_langs = [] if langs_value == "none" else [
        lang.strip() for lang in langs_value.split(",") if lang.strip()
    ]
    if not argv:
        print("사용법: python scripts/quality_gate.py {workspace} [build_subdir] [lang] [--langs en,ja|none]")
        return 1
    ws = Path(argv[0])
    build_subdir = argv[1] if len(argv) > 1 else "notes/build"
    lang = argv[2] if len(argv) > 2 else "ko"
    build_dir = ws / build_subdir
    composer = VideoComposer()

    final = ws / "video" / f"final_video_subtitled_{lang}.mp4"
    base = ws / "video" / "final_video_base.mp4"
    srt = ws / "subtitles" / f"subtitles_{lang}.srt"
    scores = {}
    notes = []

    # 1) 자막 가시성
    if final.is_file() and base.is_file() and srt.is_file():
        rep = composer.verify_burned_subtitles(base, final, srt, sample_cues=4)
        scores["자막 가시성 (실제 프레임에 자막 렌더)"] = 20 if rep["subtitles_visible"] else 0
    else:
        scores["자막 가시성 (실제 프레임에 자막 렌더)"] = 0
        notes.append("최종 영상/베이스/자막 파일이 아직 없음")

    # 2) 길이 정합
    if final.is_file() and (build_dir / "narration.wav").is_file():
        vd = float(probe(final, "format=duration")["format"]["duration"])
        nd = float(probe(build_dir / "narration.wav", "format=duration")["format"]["duration"])
        scores["길이 정합 (영상=나레이션, ±0.3s)"] = 15 if abs(vd - nd) <= 0.3 else 0
        notes.append(f"영상 {vd:.1f}s / 나레이션 {nd:.1f}s")
    else:
        scores["길이 정합 (영상=나레이션, ±0.3s)"] = 0

    # 3) 해상도
    if final.is_file():
        st = probe(final, "stream=width,height")["streams"][0]
        scores["해상도 (1920x1080)"] = 10 if (st["width"], st["height"]) == (1920, 1080) else 0
    else:
        scores["해상도 (1920x1080)"] = 0

    # 4) 장면 전환 밀도 (shots_frames 기준 평균 샷 길이)
    sf = build_dir / "shots_frames.json"
    if sf.is_file():
        shots = json.loads(sf.read_text(encoding="utf-8"))
        avg = sum(s["frames"] for s in shots) / len(shots) / 25
        scores["장면 전환 밀도 (평균 샷 ≤ 9초)"] = 15 if avg <= 9.0 else max(0, round(15 * 9 / avg))
        notes.append(f"샷 {len(shots)}개, 평균 {avg:.1f}s")
    else:
        scores["장면 전환 밀도 (평균 샷 ≤ 9초)"] = 0

    # 5) 자산 커버리지 (모든 샷에 영상 또는 이미지) + 6) 자산 믹스 적정성
    motion_dir = ws / "motion"
    img_dir = ws / "images"
    if sf.is_file():
        shots = json.loads((build_dir / "shots_frames.json").read_text(encoding="utf-8"))
        total = len(shots)
        with_video = sum(1 for s in shots if (motion_dir / f"{s['id']}.mp4").is_file())
        covered = sum(1 for s in shots if (motion_dir / f"{s['id']}.mp4").is_file()
                      or any((img_dir / f"{s['id']}{e}").is_file() for e in (".png", ".jpg", ".jpeg")))
        scores["자산 커버리지 (모든 샷에 MJ 자산)"] = round(10 * covered / total) if total else 0
        video_ratio = with_video / total if total else 0
        scores["자산 믹스 적정성 (영상 15~40%)"] = 5 if 0.15 <= video_ratio <= 0.40 else (3 if video_ratio > 0 else 0)
        notes.append(f"자산 커버 {covered}/{total} | 영상 {with_video}/{total} ({video_ratio*100:.0f}%) + 이미지켄번즈 {total-with_video}")
    else:
        scores["자산 커버리지 (모든 샷에 MJ 자산)"] = 0
        scores["자산 믹스 적정성 (영상 15~40%)"] = 0

    # 6) 나레이션 오디오
    if final.is_file():
        a = probe(final, "stream=codec_type")
        has_audio = any(s.get("codec_type") == "audio" for s in a.get("streams", []))
        scores["나레이션 오디오 존재"] = 10 if has_audio else 0
    else:
        scores["나레이션 오디오 존재"] = 0

    # 7) no-text 안전 (MJ 프롬프트에 negative 포함)
    mj_shots = ws / "notes" / "mj" / "mj_shots.json"
    if mj_shots.is_file():
        data = json.loads(mj_shots.read_text(encoding="utf-8"))
        ok = all("--no" in s["prompt"] and "text" in s["prompt"] for s in data["shots"])
        scores["no-text 안전 (프롬프트 negative 포함)"] = 15 if ok else 0
    else:
        scores["no-text 안전 (프롬프트 negative 포함)"] = 0

    # 8) 다국어 자막 (필수 게이트 — 100점 루브릭과 별개, 실패 시 게이트 FAIL)
    # 근거: docs/superpowers/specs/2026-07-17-multilang-competitor-seo-triggers-design.md #1
    multilang_lines = []
    multilang_ok = True
    if target_langs:
        source_cues = composer.parse_srt(srt) if srt.is_file() else []
        for target_lang in target_langs:
            t_path = ws / "subtitles" / f"subtitles_{target_lang}.srt"
            if not source_cues or not t_path.is_file():
                multilang_ok = False
                reason = "원본 ko SRT 없음" if not source_cues else "파일 없음"
                multilang_lines.append(f"  ❌ {target_lang}: {t_path.name} — {reason}")
                continue
            rep = validate_translated_srt(source_cues, composer.parse_srt(t_path), target_lang)
            ok = rep["status"] == "PASS"
            multilang_ok = multilang_ok and ok
            mark = "✅" if ok else "❌"
            suffix = f" issues={rep['issues']}" if rep["issues"] else ""
            multilang_lines.append(f"  {mark} {target_lang}: {t_path.name} ({rep['cue_count']}큐){suffix}")

    total_score = sum(scores[name] for name, _ in RUBRIC)
    gate_pass = total_score >= PASS_SCORE and multilang_ok
    print("=" * 52)
    print(f"  품질 게이트 — {ws.name}")
    print("=" * 52)
    for name, pts in RUBRIC:
        got = scores.get(name, 0)
        mark = "✅" if got == pts else ("⚠️" if got > 0 else "❌")
        print(f"  {mark} {name:<34} {got:>2}/{pts}")
    print("-" * 52)
    if multilang_lines:
        print("  다국어 자막 (필수 게이트):")
        for line in multilang_lines:
            print(line)
        print("-" * 52)
    verdict = "PASS ✅" if gate_pass else (
        "FAIL ❌ (95 미만)" if total_score < PASS_SCORE else "FAIL ❌ (다국어 자막)"
    )
    print(f"  총점: {total_score}/100  →  {verdict}")
    if notes:
        print("  참고:")
        for n in notes:
            print(f"    - {n}")
    print("  ※ 한글 글리프 깨짐·비주얼 품질은 사람이 눈으로 최종 확인")
    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())
