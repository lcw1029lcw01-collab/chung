# -*- coding: utf-8 -*-
"""자막 번역 잡 내보내기/조립 — 타임코드 유지 다국어 SRT.

흐름:
  1) --export : subtitles/subtitles_ko.srt → subtitles/translation_job.json
     (Claude 세션이 translations의 null을 채운다. 이미 채워진 번역은 보존)
  2) --assemble : 채워진 잡 → subtitles/subtitles_{lang}.srt + translation_report.json
     검증 FAIL이면 exit 1 (파이프라인이 감지).

실행: 프로젝트 루트에서
  python scripts/translate_subtitles.py --export {workspace} [--langs en,ja]
  python scripts/translate_subtitles.py --assemble {workspace} [--langs en,ja]
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import load_json, write_json  # noqa: E402
from engines.composition import VideoComposer  # noqa: E402
from engines.composition.subtitle_translation import (  # noqa: E402
    assemble_srt,
    build_translation_job,
    validate_translated_srt,
    validate_translation_job,
)

USAGE = """사용법: python scripts/translate_subtitles.py (--export | --assemble) {workspace} [--langs en,ja]

  --export   : subtitles/subtitles_ko.srt → subtitles/translation_job.json (번역 슬롯 비움)
  --assemble : 채워진 잡 → subtitles/subtitles_{lang}.srt + translation_report.json
  --langs    : 대상 언어 목록 (기본 en,ja)"""


def parse_args(argv: list[str]) -> dict | None:
    mode = None
    langs = ["en", "ja"]
    rest = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--export", "--assemble"):
            mode = arg[2:]
        elif arg == "--langs":
            if i + 1 >= len(argv):
                return None
            langs = [lang.strip() for lang in argv[i + 1].split(",") if lang.strip()]
            i += 1
        else:
            rest.append(arg)
        i += 1
    if mode is None or len(rest) != 1 or not langs:
        return None
    return {"mode": mode, "workspace": Path(rest[0]), "langs": langs}


def run_export(workspace: Path, langs: list[str]) -> int:
    src = workspace / "subtitles" / "subtitles_ko.srt"
    if not src.is_file():
        print(f"원본 자막이 없습니다: {src}")
        return 1
    cues = VideoComposer().parse_srt(src)
    job_path = workspace / "subtitles" / "translation_job.json"
    existing = load_json(job_path) if job_path.is_file() else None
    job = build_translation_job(cues, langs, existing_job=existing)
    write_json(job_path, job)
    print(f"번역 잡 생성: {job_path} ({job['cue_count']}큐)")
    for lang in langs:
        filled = sum(
            1 for cue in job["cues"] if (cue["translations"].get(lang) or "").strip()
        )
        print(f"  {lang}: {filled}/{job['cue_count']} 채움")
    print("다음 단계: 잡 파일의 translations를 채운 뒤 --assemble을 실행하세요.")
    return 0


def run_assemble(workspace: Path, langs: list[str]) -> int:
    job_path = workspace / "subtitles" / "translation_job.json"
    if not job_path.is_file():
        print(f"번역 잡이 없습니다: {job_path} — 먼저 --export를 실행하세요.")
        return 1
    job = load_json(job_path)
    job_report = validate_translation_job(job, langs)
    if job_report["status"] != "PASS":
        print(f"잡이 미완성입니다: {job_report['issues']}")
        return 1
    composer = VideoComposer()
    source_cues = composer.parse_srt(workspace / "subtitles" / "subtitles_ko.srt")
    reports = {}
    all_pass = True
    for lang in langs:
        srt_path = workspace / "subtitles" / f"subtitles_{lang}.srt"
        srt_path.write_text(assemble_srt(job, lang), encoding="utf-8")
        report = validate_translated_srt(source_cues, composer.parse_srt(srt_path), lang)
        reports[lang] = report
        all_pass = all_pass and report["status"] == "PASS"
        print(f"{lang}: {srt_path.name} ({report['cue_count']}큐) → {report['status']}")
        for issue in report["issues"]:
            print(f"  - {issue}")
    write_json(
        workspace / "subtitles" / "translation_report.json",
        {"reports": reports, "created_at": datetime.now(timezone.utc).isoformat()},
    )
    return 0 if all_pass else 1


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args is None:
        print(USAGE)
        return 1
    if args["mode"] == "export":
        return run_export(args["workspace"], args["langs"])
    return run_assemble(args["workspace"], args["langs"])


if __name__ == "__main__":
    sys.exit(main())
