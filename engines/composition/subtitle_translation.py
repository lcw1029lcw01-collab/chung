# -*- coding: utf-8 -*-
"""자막 번역 잡 — 타임코드를 유지한 다국어 SRT를 만들기 위한 순수 로직.

흐름: subtitles_ko.srt(문장 단위) → 번역 잡 JSON(슬롯 비움) → Claude 세션이
translations를 채움 → 언어별 SRT 조립(타임코드 원본 그대로) + 검증.
엔진은 LLM·번역 API를 호출하지 않는다 (provider_jobs의 export→fill→import 패턴).
근거: docs/superpowers/specs/2026-07-17-multilang-competitor-seo-triggers-design.md #1

순수 함수만 둔다 — 파일 IO·네트워크 없음.
"""
import re
from datetime import datetime, timezone

HANGUL_RE = re.compile(r"[가-힣]")

DEFAULT_TRANSLATION_NOTES = [
    "다큐멘터리 내레이션 톤 유지 (구어체 금지)",
    "고유명사는 통용 표기, 숫자·단위는 현지 관례",
    "큐 단위 1:1 번역 — 큐 간 내용 이동 금지",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_translation_job(
    cues: list[dict],
    target_languages: list[str],
    source_srt: str = "subtitles/subtitles_ko.srt",
    existing_job: dict | None = None,
) -> dict:
    """번역 잡을 만든다. existing_job이 있으면 이미 채워진 번역을 보존한다.

    보존 규칙: 큐 index와 source_text가 모두 같을 때만 기존 번역을 가져온다
    (원문이 바뀐 큐의 낡은 번역이 살아남으면 안 된다).
    """
    previous: dict[tuple, dict] = {}
    if existing_job:
        for cue in existing_job.get("cues", []):
            previous[(cue["index"], cue["source_text"])] = cue.get("translations", {})

    job_cues = []
    for cue in cues:
        text = str(cue["text"]).strip()
        translations: dict[str, str | None] = {lang: None for lang in target_languages}
        for lang, value in previous.get((cue["index"], text), {}).items():
            if lang in translations and value:
                translations[lang] = value
        job_cues.append(
            {
                "index": cue["index"],
                "start_seconds": float(cue["start_seconds"]),
                "end_seconds": float(cue["end_seconds"]),
                "source_text": text,
                "translations": translations,
            }
        )
    return {
        "source_lang": "ko",
        "target_languages": list(target_languages),
        "source_srt": source_srt,
        "cue_count": len(job_cues),
        "translation_notes": list(DEFAULT_TRANSLATION_NOTES),
        "cues": job_cues,
        "created_at": _now_iso(),
    }


def format_srt_timestamp(seconds: float) -> str:
    """초(float)를 SRT 타임코드(HH:MM:SS,mmm)로 바꾼다 — ms 반올림."""
    total_ms = int(round(float(seconds) * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def assemble_srt(job: dict, lang: str) -> str:
    """채워진 잡에서 lang SRT 텍스트를 만든다 — 타임코드는 원본 그대로."""
    blocks = []
    for i, cue in enumerate(job["cues"], 1):
        text = (cue["translations"].get(lang) or "").strip()
        start = format_srt_timestamp(cue["start_seconds"])
        end = format_srt_timestamp(cue["end_seconds"])
        blocks.append(f"{i}\n{start} --> {end}\n{text}")
    return "\n\n".join(blocks) + "\n"


def validate_translation_job(job: dict, langs: list[str] | None = None) -> dict:
    """잡의 번역 완결성을 검사한다 — 미번역 큐 인덱스를 언어별로 나열."""
    langs = langs if langs is not None else job.get("target_languages", [])
    issues = []
    if not job.get("cues"):
        issues.append("no_cues")
    for lang in langs:
        missing = [
            cue["index"] for cue in job.get("cues", [])
            if not (cue.get("translations", {}).get(lang) or "").strip()
        ]
        if missing:
            issues.append(f"{lang}_untranslated_cues:{missing}")
    return {"issues": issues, "status": "PASS" if not issues else "FAIL"}


def validate_translated_srt(
    source_cues: list[dict], translated_cues: list[dict], lang: str
) -> dict:
    """번역 SRT(파싱된 큐)를 원본 큐와 대조한다.

    검사: 큐 수 일치, 타임코드 완전 동일(ms 단위 비교), 빈 텍스트 없음,
    비한국어 언어에 한글 잔존 없음.
    """
    issues = []
    if len(source_cues) != len(translated_cues):
        issues.append(f"cue_count_mismatch:{len(source_cues)}!={len(translated_cues)}")
    for src, dst in zip(source_cues, translated_cues):
        same_time = (
            format_srt_timestamp(src["start_seconds"]) == format_srt_timestamp(dst["start_seconds"])
            and format_srt_timestamp(src["end_seconds"]) == format_srt_timestamp(dst["end_seconds"])
        )
        if not same_time:
            issues.append(f"cue_{dst['index']}_timecode_mismatch")
        if not str(dst.get("text", "")).strip():
            issues.append(f"cue_{dst['index']}_empty_text")
        elif lang != "ko" and HANGUL_RE.search(dst["text"]):
            issues.append(f"cue_{dst['index']}_hangul_remains")
    return {
        "lang": lang,
        "cue_count": len(translated_cues),
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }
