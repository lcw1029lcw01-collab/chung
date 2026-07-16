# 다국어 자막 · 경쟁 채널 스캐너 · SEO 심리 트리거 5축 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 타임코드를 유지한 EN/JA 자막 파이프라인(품질 게이트 필수), yt-dlp 경쟁 채널 신호 스캐너, 5축 심리 트리거 SEO 템플릿을 ADOS에 추가한다.

**Architecture:** 세 기능 모두 "엔진 = 순수 함수(네트워크·LLM 없음) / 스크립트 = IO 셸" 패턴. 번역은 provider_jobs식 잡 파일(export→Claude가 채움→assemble)로, 경쟁 데이터는 yt-dlp flat-playlist JSON으로, SEO 템플릿은 config YAML로 외부화한다.

**Tech Stack:** Python 3.10+ (표준 라이브러리 + PyYAML), unittest, yt-dlp(CLI, 스크립트에서만), ffmpeg 불필요(기존 VideoComposer.parse_srt 재사용).

**Spec:** `docs/superpowers/specs/2026-07-17-multilang-competitor-seo-triggers-design.md`

## Global Constraints

- 모든 파일 UTF-8 + `# -*- coding: utf-8 -*-` 헤더. JSON/YAML 키는 snake_case (docs/02 #7.4).
- 엔진 모듈은 네트워크·subprocess·LLM 호출 금지. 파일 IO는 스크립트/기존 core 헬퍼만.
- 테스트는 unittest 스타일(기존 파일 패턴 복사), 임시 디렉터리만 사용, 네트워크 금지.
- 전체 테스트는 프로젝트 루트에서 `python -m unittest discover -s tests -p "test_*.py"` — 기존 249개 전부 계속 통과해야 한다.
- 실행 환경은 Windows PowerShell, 프로젝트 루트 `c:\Users\이충원\Desktop\충컴퍼니`.
- 커밋은 해당 태스크가 만들거나 수정한 파일만 `git add` (작업 트리에 남의 변경이 있음 — `git add -A` 금지).

---

## Part A — 다국어 자막 (EN+JA, 파이프라인 필수)

### Task 1: 번역 잡 생성 + SRT 조립 (`subtitle_translation.py` 1/2)

**Files:**
- Create: `engines/composition/subtitle_translation.py`
- Test: `tests/test_subtitle_translation.py`

**Interfaces:**
- Consumes: `VideoComposer.parse_srt`가 만드는 큐 dict `{index:int, start_seconds:float, end_seconds:float, text:str}`
- Produces (Task 2~4가 사용):
  - `build_translation_job(cues: list[dict], target_languages: list[str], source_srt: str = "subtitles/subtitles_ko.srt", existing_job: dict | None = None) -> dict`
  - `format_srt_timestamp(seconds: float) -> str`
  - `assemble_srt(job: dict, lang: str) -> str`
  - `DEFAULT_TRANSLATION_NOTES: list[str]`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_subtitle_translation.py` 생성:

```python
# -*- coding: utf-8 -*-
"""자막 번역 잡 계층 테스트 — 순수 함수만, 파일 IO는 임시 폴더만.

실행: 프로젝트 루트에서  python -m unittest tests.test_subtitle_translation -v
"""
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.composition.subtitle_translation import (  # noqa: E402
    assemble_srt,
    build_translation_job,
    format_srt_timestamp,
)

CUES = [
    {"index": 1, "start_seconds": 0.0, "end_seconds": 4.2,
     "text": "서기 2100년, 인류는 선택의 기로에 섰습니다."},
    {"index": 2, "start_seconds": 4.2, "end_seconds": 9.87,
     "text": "이 이야기는 그 선택의 기록입니다."},
]


class TestBuildTranslationJob(unittest.TestCase):
    def test_job_structure_and_empty_slots(self):
        job = build_translation_job(CUES, ["en", "ja"])
        self.assertEqual(job["source_lang"], "ko")
        self.assertEqual(job["target_languages"], ["en", "ja"])
        self.assertEqual(job["cue_count"], 2)
        self.assertTrue(job["translation_notes"])
        first = job["cues"][0]
        self.assertEqual(first["index"], 1)
        self.assertEqual(first["source_text"], CUES[0]["text"])
        self.assertEqual(first["translations"], {"en": None, "ja": None})

    def test_existing_translations_preserved_by_index_and_text(self):
        old = build_translation_job(CUES, ["en"])
        old["cues"][0]["translations"]["en"] = "In the year 2100, ..."
        job = build_translation_job(CUES, ["en", "ja"], existing_job=old)
        self.assertEqual(job["cues"][0]["translations"]["en"], "In the year 2100, ...")
        self.assertIsNone(job["cues"][0]["translations"]["ja"])
        self.assertIsNone(job["cues"][1]["translations"]["en"])

    def test_changed_source_text_drops_stale_translation(self):
        old = build_translation_job(CUES, ["en"])
        old["cues"][0]["translations"]["en"] = "stale"
        changed = [dict(CUES[0], text="완전히 새로운 문장입니다."), CUES[1]]
        job = build_translation_job(changed, ["en"], existing_job=old)
        self.assertIsNone(job["cues"][0]["translations"]["en"])


class TestFormatSrtTimestamp(unittest.TestCase):
    def test_zero_and_plain(self):
        self.assertEqual(format_srt_timestamp(0), "00:00:00,000")
        self.assertEqual(format_srt_timestamp(1.5), "00:00:01,500")

    def test_hours_and_milliseconds(self):
        self.assertEqual(format_srt_timestamp(3661.007), "01:01:01,007")


class TestAssembleSrt(unittest.TestCase):
    def test_assemble_keeps_timecodes_and_renumbers(self):
        job = build_translation_job(CUES, ["en"])
        job["cues"][0]["translations"]["en"] = "In 2100, humanity stood at a crossroads."
        job["cues"][1]["translations"]["en"] = "This is the record of that choice."
        srt = assemble_srt(job, "en")
        blocks = srt.strip().split("\n\n")
        self.assertEqual(len(blocks), 2)
        self.assertEqual(
            blocks[0],
            "1\n00:00:00,000 --> 00:00:04,200\nIn 2100, humanity stood at a crossroads.",
        )
        self.assertEqual(
            blocks[1],
            "2\n00:00:04,200 --> 00:00:09,870\nThis is the record of that choice.",
        )
        self.assertTrue(srt.endswith("\n"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

- [ ] **Step 2: 실패 확인**

Run: `python -m unittest tests.test_subtitle_translation -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'engines.composition.subtitle_translation'`

- [ ] **Step 3: 최소 구현**

`engines/composition/subtitle_translation.py` 생성:

```python
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
```

(`HANGUL_RE`는 Task 2의 검증 함수가 쓴다 — 여기서 미리 정의해도 무해하다.)

- [ ] **Step 4: 통과 확인**

Run: `python -m unittest tests.test_subtitle_translation -v`
Expected: PASS (6 tests OK)

- [ ] **Step 5: 커밋**

```bash
git add engines/composition/subtitle_translation.py tests/test_subtitle_translation.py
git commit -m "feat: add subtitle translation job build and timecode-preserving SRT assembly"
```

---

### Task 2: 번역 검증 함수 + 라운드트립 (`subtitle_translation.py` 2/2)

**Files:**
- Modify: `engines/composition/subtitle_translation.py` (파일 끝에 함수 2개 추가)
- Test: `tests/test_subtitle_translation.py` (테스트 클래스 추가)

**Interfaces:**
- Consumes: Task 1의 함수들, `VideoComposer.parse_srt`
- Produces (Task 3~4가 사용):
  - `validate_translation_job(job: dict, langs: list[str] | None = None) -> dict` — `{"issues": list[str], "status": "PASS"|"FAIL"}`
  - `validate_translated_srt(source_cues: list[dict], translated_cues: list[dict], lang: str) -> dict` — `{"lang", "cue_count", "issues", "status"}`

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_subtitle_translation.py`의 import에 `validate_translation_job`, `validate_translated_srt`를 추가하고 (상단 import 블록의 `format_srt_timestamp,` 다음 줄들에 알파벳순 삽입), 파일 끝 `if __name__` 위에 추가:

```python
class TestValidateTranslationJob(unittest.TestCase):
    def test_untranslated_cues_listed(self):
        job = build_translation_job(CUES, ["en", "ja"])
        job["cues"][0]["translations"]["en"] = "filled"
        report = validate_translation_job(job)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("en_untranslated_cues:[2]", report["issues"])
        self.assertIn("ja_untranslated_cues:[1, 2]", report["issues"])

    def test_complete_job_passes(self):
        job = build_translation_job(CUES, ["en"])
        for cue in job["cues"]:
            cue["translations"]["en"] = "ok"
        self.assertEqual(validate_translation_job(job)["status"], "PASS")


class TestValidateTranslatedSrt(unittest.TestCase):
    def translated(self, texts: list[str]) -> list[dict]:
        return [
            {"index": i + 1, "start_seconds": c["start_seconds"],
             "end_seconds": c["end_seconds"], "text": t}
            for i, (c, t) in enumerate(zip(CUES, texts))
        ]

    def test_pass_case(self):
        report = validate_translated_srt(
            CUES, self.translated(["In 2100...", "This is the record."]), "en")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["cue_count"], 2)

    def test_cue_count_mismatch(self):
        report = validate_translated_srt(CUES, self.translated(["only one"])[:1], "en")
        self.assertIn("cue_count_mismatch:2!=1", report["issues"])

    def test_timecode_drift_detected(self):
        cues = self.translated(["a", "b"])
        cues[1]["start_seconds"] += 0.05
        report = validate_translated_srt(CUES, cues, "en")
        self.assertIn("cue_2_timecode_mismatch", report["issues"])

    def test_empty_text_and_hangul_remains(self):
        report = validate_translated_srt(CUES, self.translated(["", "번역 안 됨"]), "en")
        self.assertIn("cue_1_empty_text", report["issues"])
        self.assertIn("cue_2_hangul_remains", report["issues"])

    def test_hangul_allowed_for_ko(self):
        report = validate_translated_srt(CUES, self.translated(["가나", "다라"]), "ko")
        self.assertEqual(report["status"], "PASS")


class TestRoundTrip(unittest.TestCase):
    def test_job_to_srt_to_parse_to_validate(self):
        import tempfile

        from engines.composition import VideoComposer

        job = build_translation_job(CUES, ["en"])
        job["cues"][0]["translations"]["en"] = "In 2100, humanity stood at a crossroads."
        job["cues"][1]["translations"]["en"] = "This is the record of that choice."
        srt_text = assemble_srt(job, "en")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "subtitles_en.srt"
            path.write_text(srt_text, encoding="utf-8")
            parsed = VideoComposer().parse_srt(path)
        report = validate_translated_srt(CUES, parsed, "en")
        self.assertEqual(report["status"], "PASS", report["issues"])
```

- [ ] **Step 2: 실패 확인**

Run: `python -m unittest tests.test_subtitle_translation -v`
Expected: FAIL — `ImportError: cannot import name 'validate_translation_job'`

- [ ] **Step 3: 구현 — 파일 끝에 추가**

`engines/composition/subtitle_translation.py` 끝에:

```python
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
```

- [ ] **Step 4: 통과 확인**

Run: `python -m unittest tests.test_subtitle_translation -v`
Expected: PASS (전체 14 tests OK)

- [ ] **Step 5: 커밋**

```bash
git add engines/composition/subtitle_translation.py tests/test_subtitle_translation.py
git commit -m "feat: add translation job and translated SRT validators"
```

---

### Task 3: 번역 CLI `scripts/translate_subtitles.py`

**Files:**
- Create: `scripts/translate_subtitles.py`

**Interfaces:**
- Consumes: Task 1~2의 전 함수, `VideoComposer.parse_srt`, `core.load_json`/`write_json`
- Produces: 워크스페이스 파일 규약 — `subtitles/translation_job.json`, `subtitles/subtitles_{lang}.srt`, `subtitles/translation_report.json` (Task 4의 quality_gate가 SRT를 읽는다)

- [ ] **Step 1: 스크립트 작성** (스크립트는 얇은 IO 셸 — 리포지토리 관례상 단위 테스트 없음, 로직은 Task 1~2 테스트가 커버)

```python
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
```

- [ ] **Step 2: 스모크 테스트 (임시 워크스페이스)**

PowerShell에서:

```powershell
$ws = Join-Path $env:TEMP "ados_translate_smoke"; New-Item -ItemType Directory -Force (Join-Path $ws "subtitles") | Out-Null
@"
1
00:00:00,000 --> 00:00:04,200
서기 2100년, 인류는 선택의 기로에 섰습니다.

2
00:00:04,200 --> 00:00:09,870
이 이야기는 그 선택의 기록입니다.
"@ | Out-File -Encoding utf8 (Join-Path $ws "subtitles\subtitles_ko.srt")
python scripts/translate_subtitles.py --export $ws
python scripts/translate_subtitles.py --assemble $ws
```

Expected: export는 `번역 잡 생성: ... (2큐)` + `en: 0/2 채움` 출력 후 exit 0. assemble은 `잡이 미완성입니다: ['en_untranslated_cues:[1, 2]', ...]` 출력 후 exit 1 (미번역 상태이므로 실패가 정답).

- [ ] **Step 3: 커밋**

```bash
git add scripts/translate_subtitles.py
git commit -m "feat: add translate_subtitles CLI (job export/assemble with validation)"
```

---

### Task 4: 품질 게이트에 다국어 필수 검사 추가

**Files:**
- Modify: `scripts/quality_gate.py`

**Interfaces:**
- Consumes: `validate_translated_srt` (Task 2), 기존 `VideoComposer.parse_srt`
- Produces: `--langs en,ja`(기본) 필수 게이트 — 100점 루브릭은 그대로 두고, 다국어 실패 시 점수와 무관하게 게이트 FAIL(exit 1). `--langs none`으로 레거시 재채점 허용. (스펙의 "점수 항목 반영"은 루브릭 100점 재배분이 docs/26 근거를 깨므로, 구속력 있는 부분인 "필수·FAIL"을 별도 게이트로 구현한다.)

- [ ] **Step 1: import 추가**

`from engines.composition import VideoComposer  # noqa: E402` 아래에:

```python
from engines.composition.subtitle_translation import validate_translated_srt  # noqa: E402
```

- [ ] **Step 2: `--langs` 플래그 파싱 추가**

`main()` 안 `argv = sys.argv[1:] if argv is None else argv` 바로 다음에:

```python
    langs_value = "en,ja"
    if "--langs" in argv:
        idx = argv.index("--langs")
        langs_value = argv[idx + 1] if idx + 1 < len(argv) else "none"
        argv = argv[:idx] + argv[idx + 2:]
    target_langs = [] if langs_value == "none" else [
        lang.strip() for lang in langs_value.split(",") if lang.strip()
    ]
```

사용법 문자열(모듈 docstring과 `print("사용법: ...")`)의 `[lang]` 뒤에 `[--langs en,ja|none]`을 덧붙인다.

- [ ] **Step 3: 다국어 검사 블록 추가**

블록 `# 7) no-text 안전 ...`의 끝(`scores["no-text 안전 (프롬프트 negative 포함)"] = 0` 다음 줄)과 `total_score = ...` 사이에:

```python
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
```

- [ ] **Step 4: 최종 판정·출력 수정**

기존:

```python
    total_score = sum(scores[name] for name, _ in RUBRIC)
```

바로 다음 줄에 `gate_pass = total_score >= PASS_SCORE and multilang_ok` 추가.

기존 출력부의 `print("-" * 52)` 와 `print(f"  총점: ...")` 사이에 다국어 섹션을 넣고 총점 줄을 교체:

```python
    if multilang_lines:
        print("  다국어 자막 (필수 게이트):")
        for line in multilang_lines:
            print(line)
        print("-" * 52)
    verdict = "PASS ✅" if gate_pass else (
        "FAIL ❌ (95 미만)" if total_score < PASS_SCORE else "FAIL ❌ (다국어 자막)"
    )
    print(f"  총점: {total_score}/100  →  {verdict}")
```

(기존 `print(f"  총점: {total_score}/100  →  {'PASS ✅' if total_score >= PASS_SCORE else 'FAIL ❌ (95 미만)'}")` 줄은 삭제.)

마지막 `return 0 if total_score >= PASS_SCORE else 1` → `return 0 if gate_pass else 1`.

- [ ] **Step 5: 스모크 테스트**

```powershell
$ws = Join-Path $env:TEMP "ados_gate_smoke"; New-Item -ItemType Directory -Force $ws | Out-Null
python scripts/quality_gate.py $ws
python scripts/quality_gate.py $ws --langs none
```

Expected: 첫 실행은 루브릭 전 항목 0점 + `다국어 자막 (필수 게이트):` 섹션에 `❌ en/ja ... 파일 없음`(원본 ko SRT 없음) 표시, `FAIL ❌`, exit 1. 둘째 실행은 다국어 섹션 없이 기존과 동일한 FAIL(95 미만). 회귀 없음 확인: Task 3 스모크의 `$env:TEMP\ados_translate_smoke`에 번역을 채워 assemble한 뒤 돌리면 다국어 섹션이 ✅가 되는지도 확인 가능(선택).

- [ ] **Step 6: 커밋**

```bash
git add scripts/quality_gate.py
git commit -m "feat: enforce multilang subtitles (en,ja) in quality gate"
```

---

### Task 5: 수동 업로드 체크리스트에 자막 탭 항목 추가

**Files:**
- Modify: `engines/manual_trial/manual_trial_guide.py` (checklist_items 고정 항목 블록)
- Modify: `tests/test_real_manual_trial_preparation.py:177` (개수 단언 +3 → +4)

**Interfaces:**
- Consumes: 없음 (독립 수정)
- Produces: 체크리스트 고정 항목 4개 (기존 3개 + 자막 탭 업로드)

- [ ] **Step 1: 테스트 단언 먼저 수정 (TDD — 기대치 갱신)**

`tests/test_real_manual_trial_preparation.py` 177행:

```python
        self.assertEqual(len(checklist["items"]), len(files) + 3)
```

→

```python
        self.assertEqual(len(checklist["items"]), len(files) + 4)
```

- [ ] **Step 2: 실패 확인**

Run: `python -m unittest tests.test_real_manual_trial_preparation -v`
Expected: FAIL — 해당 테스트에서 `AssertionError: N != N+1`

- [ ] **Step 3: 구현**

`engines/manual_trial/manual_trial_guide.py`의 고정 항목 블록:

```python
            {"checklist_id": f"CL{len(expected) + 3:03d}",
             "description": "finalize 스크립트 실행 후 업로드 패키지 확인", "done": False},
        ]
```

→

```python
            {"checklist_id": f"CL{len(expected) + 3:03d}",
             "description": "finalize 스크립트 실행 후 업로드 패키지 확인", "done": False},
            {"checklist_id": f"CL{len(expected) + 4:03d}",
             "description": "유튜브 스튜디오 자막 탭에 다국어 SRT 업로드 (subtitles_en/ja.srt)",
             "done": False},
        ]
```

- [ ] **Step 4: 통과 확인**

Run: `python -m unittest tests.test_real_manual_trial_preparation -v`
Expected: PASS (전체 OK)

- [ ] **Step 5: 커밋**

```bash
git add engines/manual_trial/manual_trial_guide.py tests/test_real_manual_trial_preparation.py
git commit -m "feat: add multilang SRT upload step to manual trial checklist"
```

---

## Part B — 경쟁 채널 스캐너

### Task 6: 파싱 + 채널 분석 (`competitor_scanner.py` 1/2)

**Files:**
- Create: `engines/research/competitor_scanner.py`
- Test: `tests/test_competitor_scanner.py`

**Interfaces:**
- Consumes: yt-dlp `-J --flat-playlist` 원본 dict (스크립트가 넘겨줌)
- Produces (Task 7~8이 사용):
  - `parse_flat_playlist(raw: dict) -> dict` — `{channel_name, channel_url, videos: list[dict], skipped_count}`
  - `analyze_channel(parsed: dict, recent_n: int = 25) -> dict` — `{channel_name, channel_url, video_count_scanned, skipped_count, avg_views, median_views, videos}` (각 video에 `multiple_vs_avg/multiple_vs_median/signal` 추가)
  - `SIGNAL_THRESHOLD = 2.0`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_competitor_scanner.py` 생성:

```python
# -*- coding: utf-8 -*-
"""경쟁 채널 스캐너 테스트 — 픽스처 dict만 사용, 네트워크 없음.

실행: 프로젝트 루트에서  python -m unittest tests.test_competitor_scanner -v
"""
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.research.competitor_scanner import (  # noqa: E402
    analyze_channel,
    parse_flat_playlist,
)

RAW = {
    "channel": "미래탐사단",
    "channel_url": "https://www.youtube.com/@future-lab",
    "entries": [
        {"id": "v1", "title": "영상 1", "url": "https://youtu.be/v1",
         "view_count": 1000, "duration": 600, "upload_date": "20260701"},
        {"id": "v2", "title": "영상 2", "view_count": 2000, "duration": 700},
        {"id": "v3", "title": "영상 3", "view_count": 3000, "duration": 800},
        {"id": "v4", "title": "떡상 영상", "view_count": 10000, "duration": 900},
        {"id": "v5", "title": "멤버십 영상", "view_count": None},
        None,
    ],
}


class TestParseFlatPlaylist(unittest.TestCase):
    def test_parse_and_skip(self):
        parsed = parse_flat_playlist(RAW)
        self.assertEqual(parsed["channel_name"], "미래탐사단")
        self.assertEqual(len(parsed["videos"]), 4)
        self.assertEqual(parsed["skipped_count"], 2)

    def test_url_fallback_from_id(self):
        parsed = parse_flat_playlist(RAW)
        self.assertEqual(parsed["videos"][1]["url"], "https://www.youtube.com/watch?v=v2")

    def test_empty_entries(self):
        parsed = parse_flat_playlist({"channel": "빈 채널", "entries": None})
        self.assertEqual(parsed["videos"], [])
        self.assertEqual(parsed["skipped_count"], 0)


class TestAnalyzeChannel(unittest.TestCase):
    def test_avg_median_and_multiples(self):
        analysis = analyze_channel(parse_flat_playlist(RAW))
        # views [1000, 2000, 3000, 10000] → avg 4000, median 2500
        self.assertEqual(analysis["avg_views"], 4000.0)
        self.assertEqual(analysis["median_views"], 2500.0)
        top = analysis["videos"][3]
        self.assertEqual(top["multiple_vs_median"], 4.0)
        self.assertEqual(top["multiple_vs_avg"], 2.5)
        self.assertEqual(top["signal"], "HIGH")
        self.assertEqual(analysis["videos"][0]["signal"], "NORMAL")

    def test_threshold_boundary_is_high(self):
        raw = {"channel": "경계", "entries": [
            {"id": "a", "view_count": 100}, {"id": "b", "view_count": 100},
            {"id": "c", "view_count": 200},
        ]}
        analysis = analyze_channel(parse_flat_playlist(raw))
        # median 100 → 200은 정확히 2.0배 → HIGH (경계 포함)
        self.assertEqual(analysis["videos"][2]["signal"], "HIGH")

    def test_recent_n_slices_from_front(self):
        analysis = analyze_channel(parse_flat_playlist(RAW), recent_n=2)
        self.assertEqual(analysis["video_count_scanned"], 2)
        self.assertEqual(analysis["avg_views"], 1500.0)

    def test_empty_channel_no_division_error(self):
        analysis = analyze_channel(parse_flat_playlist({"entries": []}))
        self.assertEqual(analysis["video_count_scanned"], 0)
        self.assertEqual(analysis["avg_views"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

- [ ] **Step 2: 실패 확인**

Run: `python -m unittest tests.test_competitor_scanner -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'engines.research.competitor_scanner'`

- [ ] **Step 3: 구현**

`engines/research/competitor_scanner.py` 생성:

```python
# -*- coding: utf-8 -*-
"""경쟁 채널 스캐너 — yt-dlp flat-playlist 출력을 분석해 주제 신호를 뽑는다.

핵심 신호: 채널 최근 N편의 중앙값 조회수 대비 배수(multiple_vs_median) ≥ 2.0
→ HIGH. 바이럴 1편이 평균을 왜곡하므로 중앙값이 기본이고 평균 배수는 병기한다.
근거: docs/superpowers/specs/2026-07-17-multilang-competitor-seo-triggers-design.md #2

순수 함수만 둔다 — 네트워크·subprocess 없음 (yt-dlp 실행은 scripts/scan_competitors.py).
"""
from statistics import median

SIGNAL_THRESHOLD = 2.0


def parse_flat_playlist(raw: dict) -> dict:
    """yt-dlp `-J --flat-playlist` 출력을 정규화한다.

    view_count가 없는 항목(멤버십·예정·비공개)은 건너뛰고 skipped_count에 센다.
    """
    entries = raw.get("entries") or []
    videos = []
    skipped = 0
    for entry in entries:
        if not entry or entry.get("view_count") is None:
            skipped += 1
            continue
        video_id = entry.get("id", "")
        videos.append(
            {
                "video_id": video_id,
                "title": entry.get("title", ""),
                "url": entry.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                "view_count": int(entry["view_count"]),
                "duration_seconds": entry.get("duration"),
                "upload_date": entry.get("upload_date"),
            }
        )
    return {
        "channel_name": raw.get("channel") or raw.get("uploader") or raw.get("title") or "",
        "channel_url": raw.get("channel_url") or raw.get("webpage_url") or "",
        "videos": videos,
        "skipped_count": skipped,
    }


def analyze_channel(parsed: dict, recent_n: int = 25) -> dict:
    """최근 N편 기준 평균/중앙값과 영상별 배수·신호를 계산한다."""
    recent = parsed["videos"][:recent_n]
    views = [video["view_count"] for video in recent]
    avg = (sum(views) / len(views)) if views else 0.0
    med = float(median(views)) if views else 0.0
    analyzed = []
    for video in recent:
        multiple_avg = round(video["view_count"] / avg, 2) if avg else 0.0
        multiple_med = round(video["view_count"] / med, 2) if med else 0.0
        analyzed.append(
            {
                **video,
                "multiple_vs_avg": multiple_avg,
                "multiple_vs_median": multiple_med,
                "signal": "HIGH" if multiple_med >= SIGNAL_THRESHOLD else "NORMAL",
            }
        )
    return {
        "channel_name": parsed["channel_name"],
        "channel_url": parsed["channel_url"],
        "video_count_scanned": len(recent),
        "skipped_count": parsed.get("skipped_count", 0),
        "avg_views": round(avg, 1),
        "median_views": med,
        "videos": analyzed,
    }
```

- [ ] **Step 4: 통과 확인**

Run: `python -m unittest tests.test_competitor_scanner -v`
Expected: PASS (7 tests OK)

- [ ] **Step 5: 커밋**

```bash
git add engines/research/competitor_scanner.py tests/test_competitor_scanner.py
git commit -m "feat: add competitor channel parser and median-multiple analyzer"
```

---

### Task 7: 리포트 + CSV (`competitor_scanner.py` 2/2)

**Files:**
- Modify: `engines/research/competitor_scanner.py` (파일 끝에 추가)
- Test: `tests/test_competitor_scanner.py` (클래스 추가)

**Interfaces:**
- Consumes: `analyze_channel` 결과 list
- Produces (Task 8이 사용):
  - `build_report(analyses: list[dict]) -> dict` — `{channel_count, channels(각각 videos 포함), high_signals(중앙값 배수 내림차순)}`
  - `report_to_csv_rows(report: dict) -> list[list]` — 헤더 `CSV_COLUMNS` + 전 영상 행
  - `CSV_COLUMNS: list[str]`

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_competitor_scanner.py` import에 `build_report`, `report_to_csv_rows`, `CSV_COLUMNS` 추가 후, `if __name__` 위에:

```python
class TestBuildReport(unittest.TestCase):
    def analyses(self):
        second = {"channel": "채널B", "entries": [
            {"id": "b1", "view_count": 100}, {"id": "b2", "view_count": 100},
            {"id": "b3", "title": "B 떡상", "view_count": 500},
        ]}
        return [
            analyze_channel(parse_flat_playlist(RAW)),
            analyze_channel(parse_flat_playlist(second)),
        ]

    def test_high_signals_ranked_desc(self):
        report = build_report(self.analyses())
        self.assertEqual(report["channel_count"], 2)
        multiples = [s["multiple_vs_median"] for s in report["high_signals"]]
        self.assertEqual(multiples, sorted(multiples, reverse=True))
        self.assertEqual(report["high_signals"][0]["title"], "B 떡상")  # 5.0배
        self.assertEqual(report["high_signals"][0]["channel_name"], "채널B")

    def test_channel_summary_counts(self):
        report = build_report(self.analyses())
        first = report["channels"][0]
        self.assertEqual(first["high_signal_count"], 1)
        self.assertEqual(len(first["videos"]), 4)


class TestCsvRows(unittest.TestCase):
    def test_header_and_sorted_rows(self):
        report = build_report([analyze_channel(parse_flat_playlist(RAW))])
        rows = report_to_csv_rows(report)
        self.assertEqual(rows[0], CSV_COLUMNS)
        self.assertEqual(len(rows), 1 + 4)
        self.assertEqual(rows[1][1], "떡상 영상")  # 배수 내림차순 첫 행
        self.assertEqual(rows[1][6], "HIGH")

    def test_missing_optional_fields_blank(self):
        report = build_report([analyze_channel(parse_flat_playlist(RAW))])
        rows = report_to_csv_rows(report)
        # v2는 upload_date가 없다 → 빈 문자열
        v2_row = next(r for r in rows[1:] if r[1] == "영상 2")
        self.assertEqual(v2_row[7], "")
```

- [ ] **Step 2: 실패 확인**

Run: `python -m unittest tests.test_competitor_scanner -v`
Expected: FAIL — `ImportError: cannot import name 'build_report'`

- [ ] **Step 3: 구현 — 파일 끝에 추가**

```python
CSV_COLUMNS = [
    "channel", "title", "url", "view_count",
    "multiple_vs_median", "multiple_vs_avg", "signal",
    "upload_date", "duration_seconds",
]


def build_report(analyses: list[dict]) -> dict:
    """채널별 요약(전 영상 포함) + 전 채널 HIGH 신호 랭킹(중앙값 배수 내림차순)."""
    signals = [
        {**video, "channel_name": analysis["channel_name"]}
        for analysis in analyses
        for video in analysis["videos"]
        if video["signal"] == "HIGH"
    ]
    signals.sort(key=lambda video: video["multiple_vs_median"], reverse=True)
    return {
        "channel_count": len(analyses),
        "channels": [
            {
                "channel_name": analysis["channel_name"],
                "channel_url": analysis["channel_url"],
                "video_count_scanned": analysis["video_count_scanned"],
                "skipped_count": analysis["skipped_count"],
                "avg_views": analysis["avg_views"],
                "median_views": analysis["median_views"],
                "high_signal_count": sum(
                    1 for video in analysis["videos"] if video["signal"] == "HIGH"
                ),
                "videos": analysis["videos"],
            }
            for analysis in analyses
        ],
        "high_signals": signals,
    }


def report_to_csv_rows(report: dict) -> list[list]:
    """CSV 저장용 평탄화 — 헤더 + 전 채널 전 영상(중앙값 배수 내림차순)."""
    rows: list[list] = [list(CSV_COLUMNS)]
    pairs = [
        (channel["channel_name"], video)
        for channel in report["channels"]
        for video in channel["videos"]
    ]
    pairs.sort(key=lambda pair: pair[1]["multiple_vs_median"], reverse=True)
    for channel_name, video in pairs:
        rows.append([
            channel_name, video["title"], video["url"], video["view_count"],
            video["multiple_vs_median"], video["multiple_vs_avg"], video["signal"],
            video.get("upload_date") or "", video.get("duration_seconds") or "",
        ])
    return rows
```

- [ ] **Step 4: 통과 확인**

Run: `python -m unittest tests.test_competitor_scanner -v`
Expected: PASS (11 tests OK)

- [ ] **Step 5: 커밋**

```bash
git add engines/research/competitor_scanner.py tests/test_competitor_scanner.py
git commit -m "feat: add competitor scan report builder and CSV flattening"
```

---

### Task 8: 스캔 CLI `scripts/scan_competitors.py`

**Files:**
- Create: `scripts/scan_competitors.py`

**Interfaces:**
- Consumes: Task 6~7의 전 함수, `core.load_yaml`/`write_json`
- Produces: `channels/{id}/research/competitor_scan_YYYYMMDD/` 아래 `raw_{슬러그}.json` + `report.json` + `report.csv`. 선택 입력 `channels/{id}/competitors.yaml` (`competitors: [{name, url}]`)

- [ ] **Step 1: 스크립트 작성** (얇은 IO 셸 — 단위 테스트 없음, 로직은 Task 6~7이 커버)

```python
# -*- coding: utf-8 -*-
"""경쟁 채널 스캔 — yt-dlp로 채널별 최근 영상을 전수 추출해 신호를 뽑는다.

API 키 불필요. 채널당 `yt-dlp --flat-playlist -J {url}/videos` 1회 실행.
출력: report.json(채널 요약 + HIGH 신호 랭킹) + report.csv + raw_{슬러그}.json.

실행: 프로젝트 루트에서
  python scripts/scan_competitors.py {channel_url} [{channel_url} ...] [--channel {id}] [--recent-n 25]
  URL 없이 --channel만 주면 channels/{id}/competitors.yaml의 competitors 목록을 쓴다.
"""
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import load_yaml, write_json  # noqa: E402
from engines.research.competitor_scanner import (  # noqa: E402
    analyze_channel,
    build_report,
    parse_flat_playlist,
    report_to_csv_rows,
)

USAGE = """사용법: python scripts/scan_competitors.py {channel_url} [...] [--channel {id}] [--recent-n 25]

  channel_url : 유튜브 채널 URL (여러 개 가능)
  --channel   : 채널 id — 출력 위치(channels/{id}/research/)와
                URL 미지정 시 channels/{id}/competitors.yaml 목록 사용
  --recent-n  : 채널당 분석할 최근 영상 수 (기본 25)"""


def slugify(name: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z가-힣]+", "-", name).strip("-").lower()
    return slug or "channel"


def videos_url(url: str) -> str:
    url = url.rstrip("/")
    return url if url.endswith("/videos") else url + "/videos"


def run_yt_dlp(url: str) -> dict:
    cmd = [
        "yt-dlp", "--flat-playlist", "-J",
        "--extractor-args", "youtubetab:approximate_date",
        videos_url(url),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "yt-dlp 실패").strip()[-500:])
    return json.loads(result.stdout)


def parse_args(argv: list[str]) -> dict | None:
    urls = []
    channel_id = None
    recent_n = 25
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--channel":
            if i + 1 >= len(argv):
                return None
            channel_id = argv[i + 1]
            i += 1
        elif arg == "--recent-n":
            if i + 1 >= len(argv):
                return None
            recent_n = int(argv[i + 1])
            i += 1
        else:
            urls.append(arg)
        i += 1
    if not urls and channel_id:
        config_path = PROJECT_ROOT / "channels" / channel_id / "competitors.yaml"
        if config_path.is_file():
            config = load_yaml(config_path) or {}
            urls = [c["url"] for c in config.get("competitors", []) if c.get("url")]
    if not urls:
        return None
    return {"urls": urls, "channel_id": channel_id, "recent_n": recent_n}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args is None:
        print(USAGE)
        return 1

    date_tag = datetime.now(timezone.utc).strftime("%Y%m%d")
    if args["channel_id"]:
        out_dir = PROJECT_ROOT / "channels" / args["channel_id"] / "research" / f"competitor_scan_{date_tag}"
    else:
        out_dir = Path.cwd() / f"competitor_scan_{date_tag}"
    out_dir.mkdir(parents=True, exist_ok=True)

    analyses = []
    failed = []
    for url in args["urls"]:
        try:
            raw = run_yt_dlp(url)
        except FileNotFoundError:
            print("yt-dlp가 설치되어 있지 않습니다. 설치: pip install yt-dlp")
            return 1
        except (RuntimeError, json.JSONDecodeError) as exc:
            print(f"⚠️ 추출 실패, 건너뜀: {url}\n   {exc}")
            failed.append({"url": url, "error": str(exc)})
            continue
        parsed = parse_flat_playlist(raw)
        write_json(out_dir / f"raw_{slugify(parsed['channel_name'])}.json", raw)
        analyses.append(analyze_channel(parsed, recent_n=args["recent_n"]))
        print(f"✅ {parsed['channel_name']}: {len(parsed['videos'])}편 추출")

    if not analyses:
        print("분석할 채널이 없습니다.")
        return 1

    report = build_report(analyses)
    report["failed_channels"] = failed
    report["recent_n"] = args["recent_n"]
    report["created_at"] = datetime.now(timezone.utc).isoformat()
    write_json(out_dir / "report.json", report)
    with (out_dir / "report.csv").open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(report_to_csv_rows(report))

    print(f"\n리포트 저장: {out_dir}")
    print(f"HIGH 신호 {len(report['high_signals'])}개 (중앙값 대비 ≥2.0배):")
    for signal in report["high_signals"][:10]:
        print(f"  {signal['multiple_vs_median']:>5.1f}x  [{signal['channel_name']}] {signal['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 사용법 스모크**

Run: `python scripts/scan_competitors.py`
Expected: USAGE 출력 후 exit 1.

- [ ] **Step 3: (선택, 네트워크 필요) 실채널 스모크**

Run: `python scripts/scan_competitors.py https://www.youtube.com/@kurzgesagt --recent-n 10`
Expected: `✅ ... 편 추출` 후 `competitor_scan_YYYYMMDD/`에 raw/report.json/report.csv 생성, HIGH 신호 목록 출력. (오프라인이면 건너뛰고 다음 태스크 진행 — 엔진 로직은 이미 테스트됨.)

- [ ] **Step 4: 커밋**

```bash
git add scripts/scan_competitors.py
git commit -m "feat: add competitor channel scan CLI (yt-dlp flat-playlist)"
```

---

## Part C — SEO 심리 트리거 5축

### Task 9: 트리거 템플릿 config + 로더

**Files:**
- Create: `config/seo_templates.yaml`
- Modify: `engines/seo/seo_engine.py` (로더 함수와 상수 추가 — 기존 코드는 이 태스크에서 아직 유지)
- Modify: `engines/seo/__init__.py`
- Test: `tests/test_scene_script_world_seo.py` (로더 테스트 추가 + config 복사 목록 갱신)

**Interfaces:**
- Consumes: `core.load_yaml`, `ADOSPathManager.find_project_root`
- Produces (Task 10이 사용):
  - `TRIGGER_AXES = ["loss_fear", "curiosity_gap", "authority_proof", "efficiency_gain", "desire_identity"]`
  - `load_seo_templates(start: str | Path | None = None) -> dict` — 축 이름 → `{label, ko_titles, en_titles, thumbnail_texts}`

- [ ] **Step 1: config 파일 작성**

`config/seo_templates.yaml` 생성:

```yaml
# SEO 제목·썸네일 템플릿 — 5대 심리 트리거 축.
# 출처: 썸네일 170개 → 5대 심리 카테고리 압축(비블 강연) + 기존 formula_v1 템플릿 재배치.
# 원칙: 다큐 채널 신뢰성 유지 — 과장·허위형 카피 금지, 축의 심리만 차용한다.
# 변수: {topic} {topic_en} {year}
triggers:
  loss_fear:            # 금기, 놓침, 기간 한정
    label: "손실·공포"
    ko_titles:
      - "{topic} — 지금 모르면 늦는 이야기"
      - "인류가 외면해온 진실: {topic}"
      - "{year}년, 준비되지 않은 인류에게 벌어질 일 | {topic}"
      - "{topic} — 우리가 잃게 될 것들"
    en_titles:
      - "{topic_en} — The Story We Can't Afford to Ignore"
      - "The Truth Humanity Keeps Avoiding: {topic_en}"
      - "What Happens to an Unprepared Humanity in {year} | {topic_en}"
      - "{topic_en} — What We Stand to Lose"
    thumbnail_texts:
      - "모르면 늦는다"
      - "우리가 잃게 될 것"
  curiosity_gap:        # 미공개, 반전
    label: "호기심·은폐"
    ko_titles:
      - "{topic} — 교과서에 없는 이야기"
      - "아무도 말하지 않는 {topic}의 반전"
      - "{topic}, 결말은 예상과 다르다"
      - "과학자들도 의견이 갈리는 질문: {topic}"
    en_titles:
      - "{topic_en} — The Story Textbooks Left Out"
      - "The Twist Nobody Talks About: {topic_en}"
      - "{topic_en} — The Ending Isn't What You Expect"
      - "The Question That Divides Scientists: {topic_en}"
    thumbnail_texts:
      - "교과서에 없는 이야기"
      - "결말이 다르다"
  authority_proof:      # 내부자 목격, 수치·데이터
    label: "권위·증거"
    ko_titles:
      - "{topic} — 과학이 예측한 미래"
      - "{topic}: 데이터가 가리키는 세 가지 시나리오"
      - "미래 인류 보고서 — {topic}"
      - "과학이 그리는 {year}년 | {topic}"
    en_titles:
      - "{topic_en} — What Scientists Predict"
      - "{topic_en}: Three Scenarios the Data Points To"
      - "Future Humanity Report — {topic_en}"
      - "Science Predicts {year} | {topic_en}"
    thumbnail_texts:
      - "과학자들의 대답"
      - "데이터가 가리키는 미래"
  efficiency_gain:      # 시간 확보, 압축
    label: "효율·이득"
    ko_titles:
      - "{topic}, 25분 만에 이해하기"
      - "{topic} — 핵심만 담은 미래 보고서"
      - "이 영상 하나로 정리되는 {topic}"
      - "{topic}: 100년의 변화를 한 편에"
    en_titles:
      - "{topic_en}, Explained in 25 Minutes"
      - "{topic_en} — The Essential Future Report"
      - "{topic_en}, All in One Documentary"
      - "{topic_en}: A Century of Change in One Film"
    thumbnail_texts:
      - "한 편으로 정리"
      - "25분 완전 정리"
  desire_identity:      # 변신, 특별함
    label: "욕망·정체성"
    ko_titles:
      - "{topic} — 당신의 후손 이야기"
      - "인류의 다음 챕터: {topic}"
      - "{topic} | 진화는 멈추지 않는다"
      - "우리는 어떤 존재가 될까 — {topic}"
    en_titles:
      - "{topic_en} — The Story of Your Descendants"
      - "Humanity's Next Chapter: {topic_en}"
      - "{topic_en} | Evolution Never Stops"
      - "What Will We Become — {topic_en}"
    thumbnail_texts:
      - "인류의 다음 모습"
      - "당신의 후손"
```

- [ ] **Step 2: 실패하는 테스트 추가**

`tests/test_scene_script_world_seo.py`:

(a) `make_project_in_temp_root`의 config 복사 목록 갱신:

```python
    for config_name in ("documentary_engine.yaml", "scene_script_engine.yaml"):
```

→

```python
    for config_name in (
        "documentary_engine.yaml", "scene_script_engine.yaml", "seo_templates.yaml"
    ):
```

(b) import 블록의 `from engines.seo import SEOEngine  # noqa: E402` →

```python
from engines.seo import SEOEngine, TRIGGER_AXES, load_seo_templates  # noqa: E402
```

(c) `TestSEOEngine` 클래스에 테스트 추가:

```python
    def test_load_seo_templates_axes(self):
        triggers = load_seo_templates(self.project_path)
        self.assertEqual(set(triggers), set(TRIGGER_AXES))
        for axis in TRIGGER_AXES:
            self.assertGreaterEqual(len(triggers[axis]["ko_titles"]), 4)
            self.assertGreaterEqual(len(triggers[axis]["en_titles"]), 4)
            self.assertGreaterEqual(len(triggers[axis]["thumbnail_texts"]), 1)

    def test_seo_requires_templates_config(self):
        run_until_direction(self.project_path)
        (self.root / "config" / "seo_templates.yaml").unlink()
        with self.assertRaises(ADOSFileNotFoundError):
            load_seo_templates(self.project_path)
```

- [ ] **Step 3: 실패 확인**

Run: `python -m unittest tests.test_scene_script_world_seo -v`
Expected: FAIL — `ImportError: cannot import name 'TRIGGER_AXES'`

- [ ] **Step 4: 구현**

`engines/seo/seo_engine.py` — import 블록을 다음으로 교체:

```python
from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSPathManager,
    ADOSValidationError,
    ADOSValidator,
    load_json,
    load_yaml,
    write_json,
)
```

`SEO_PACKAGE_FILE = "seo_package.json"` 아래에 추가:

```python
SEO_TEMPLATES_FILE = "seo_templates.yaml"

# 5대 심리 트리거 축 — A/B 짝짓기·검증의 고정 순서
TRIGGER_AXES = [
    "loss_fear",
    "curiosity_gap",
    "authority_proof",
    "efficiency_gain",
    "desire_identity",
]


def load_seo_templates(start: str | Path | None = None) -> dict:
    """config/seo_templates.yaml의 triggers를 읽는다. 없으면 에러 (config 필수)."""
    root = ADOSPathManager.find_project_root(start)
    path = root / "config" / SEO_TEMPLATES_FILE
    if not path.is_file():
        raise ADOSFileNotFoundError(
            f"SEO 템플릿 config가 없습니다: {path}",
            location="load_seo_templates",
            suggested_fix="config/seo_templates.yaml을 생성하세요.",
        )
    triggers = (load_yaml(path) or {}).get("triggers") or {}
    missing = [axis for axis in TRIGGER_AXES if axis not in triggers]
    if missing:
        raise ADOSValidationError(
            f"SEO 템플릿에 누락된 트리거 축: {missing}",
            location="load_seo_templates",
            suggested_fix="5축을 모두 채우세요: " + ", ".join(TRIGGER_AXES),
        )
    return triggers
```

`engines/seo/__init__.py`를 다음으로 교체:

```python
# -*- coding: utf-8 -*-
from .seo_engine import SEOEngine, TRIGGER_AXES, load_seo_templates

__all__ = ["SEOEngine", "TRIGGER_AXES", "load_seo_templates"]
```

- [ ] **Step 5: 통과 확인**

Run: `python -m unittest tests.test_scene_script_world_seo -v`
Expected: PASS (기존 + 신규 2개 OK — 기존 formula_v1 경로는 아직 그대로라 전부 통과)

- [ ] **Step 6: 커밋**

```bash
git add config/seo_templates.yaml engines/seo/seo_engine.py engines/seo/__init__.py tests/test_scene_script_world_seo.py
git commit -m "feat: add 5-axis psychological trigger SEO template config and loader"
```

---

### Task 10: SEO 패키지 v2 — 태그된 후보 + A/B 세트 + 검증

**Files:**
- Modify: `engines/seo/seo_engine.py`
- Test: `tests/test_scene_script_world_seo.py` (`TestSEOEngine` 갱신)

**Interfaces:**
- Consumes: Task 9의 `load_seo_templates`, `TRIGGER_AXES`
- Produces: `seo_package.json` v2 스키마 — `title_candidates_ko/en`·`thumbnail_text_candidates`는 `{"text": str, "trigger": str}` 목록, 신규 `ab_test_sets`(3세트, 각 `{"set_id", "a", "b"}` — a/b는 후보 dict), `seo_mode: "formula_v2_triggers"`

- [ ] **Step 1: 실패하는 테스트로 갱신**

`TestSEOEngine.test_seo_package_counts`를 다음으로 교체:

```python
    def test_seo_package_counts(self):
        run_until_direction(self.project_path)
        SceneScriptEngine().create_dummy_scene_script(self.project_path)
        engine = SEOEngine()
        package = engine.create_seo_package(self.project_path)
        self.assertTrue(engine.validate_seo_package(self.project_path))
        self.assertEqual(package["seo_mode"], "formula_v2_triggers")
        self.assertEqual(len(package["title_candidates_ko"]), 20)
        self.assertEqual(len(package["title_candidates_en"]), 20)
        for key in ("title_candidates_ko", "title_candidates_en"):
            axes = {candidate["trigger"] for candidate in package[key]}
            self.assertEqual(axes, set(TRIGGER_AXES))
            for candidate in package[key]:
                self.assertNotIn("{topic", candidate["text"])  # 변수 치환 완료
        self.assertGreaterEqual(len(package["thumbnail_text_candidates"]), 5)
        self.assertGreaterEqual(len(package["tags"]), 10)
        self.assertGreaterEqual(len(package["chapters"]), 3)
        self.assertIn("[챕터]", package["description"])

    def test_ab_test_sets_pair_different_axes(self):
        run_until_direction(self.project_path)
        package = SEOEngine().create_seo_package(self.project_path)
        sets = package["ab_test_sets"]
        self.assertEqual(len(sets), 3)
        self.assertEqual([s["set_id"] for s in sets], ["AB1", "AB2", "AB3"])
        for ab_set in sets:
            self.assertNotEqual(ab_set["a"]["trigger"], ab_set["b"]["trigger"])
            self.assertTrue(ab_set["a"]["text"] and ab_set["b"]["text"])
```

- [ ] **Step 2: 실패 확인**

Run: `python -m unittest tests.test_scene_script_world_seo.TestSEOEngine -v`
Expected: FAIL — `KeyError: 'seo_mode' == 'formula_v1'` 불일치 또는 `'trigger'` KeyError

- [ ] **Step 3: 구현**

`engines/seo/seo_engine.py`:

(a) 기존 상수 `TITLE_TEMPLATES_KO`, `TITLE_TEMPLATES_EN`, `THUMBNAIL_TEMPLATES` 세 블록 전체 삭제 (`BASE_TAGS`는 유지).

(b) `SEO_REQUIRED_FIELDS`에 `"ab_test_sets",` 추가 (`"pinned_comment",` 다음 줄).

(c) 모듈 함수 추가 (`load_seo_templates` 아래):

```python
def _build_ab_test_sets(title_candidates: list[dict]) -> list[dict]:
    """서로 다른 축끼리 짝지은 A/B 3세트 — 결정적 규칙 (스펙 #3).

    (1축 첫 vs 2축 첫), (3축 첫 vs 4축 첫), (5축 첫 vs 1축 둘째).
    """
    first_by_axis: dict[str, dict] = {}
    second_by_axis: dict[str, dict] = {}
    for candidate in title_candidates:
        axis = candidate["trigger"]
        if axis not in first_by_axis:
            first_by_axis[axis] = candidate
        elif axis not in second_by_axis:
            second_by_axis[axis] = candidate
    pairs = [
        (first_by_axis[TRIGGER_AXES[0]], first_by_axis[TRIGGER_AXES[1]]),
        (first_by_axis[TRIGGER_AXES[2]], first_by_axis[TRIGGER_AXES[3]]),
        (first_by_axis[TRIGGER_AXES[4]], second_by_axis[TRIGGER_AXES[0]]),
    ]
    return [
        {"set_id": f"AB{i}", "a": a, "b": b} for i, (a, b) in enumerate(pairs, 1)
    ]
```

(d) `create_seo_package`에서 `chapters = self._build_chapters(project_path)` 위에 추가:

```python
        triggers = load_seo_templates(project_path)
        title_candidates_ko = [
            {"text": template.format(topic=topic, year=year), "trigger": axis}
            for axis in TRIGGER_AXES
            for template in triggers[axis]["ko_titles"]
        ]
        title_candidates_en = [
            {"text": template.format(topic_en=topic_en, year=year), "trigger": axis}
            for axis in TRIGGER_AXES
            for template in triggers[axis]["en_titles"]
        ]
        thumbnail_candidates = [
            {"text": template.format(topic=topic, year=year), "trigger": axis}
            for axis in TRIGGER_AXES
            for template in triggers[axis]["thumbnail_texts"]
        ]
```

(e) `package = {...}` dict에서 아래 항목들을 교체:

- `"seo_mode": "formula_v1",` → `"seo_mode": "formula_v2_triggers",`
- `"title_candidates_ko": [...]` (format 리스트 컴프리헨션 블록) → `"title_candidates_ko": title_candidates_ko,`
- `"title_candidates_en": [...]` → `"title_candidates_en": title_candidates_en,`
- `"thumbnail_text_candidates": [...]` → `"thumbnail_text_candidates": thumbnail_candidates,`
- `"pinned_comment": (...)` 항목 바로 다음에 `"ab_test_sets": _build_ab_test_sets(title_candidates_ko),` 추가

(f) `validate_seo_package`의 후보 검증 루프 교체:

```python
        for key in ("title_candidates_ko", "title_candidates_en"):
            if len(package[key]) < 20:
                raise ADOSValidationError(
                    f"{key}가 20개 미만입니다: {len(package[key])}개",
                    location="SEOEngine.validate_seo_package",
                    suggested_fix="제목 템플릿을 20개 이상 유지하세요.",
                )
```

→

```python
        for key in ("title_candidates_ko", "title_candidates_en"):
            candidates = package[key]
            if len(candidates) < 20:
                raise ADOSValidationError(
                    f"{key}가 20개 미만입니다: {len(candidates)}개",
                    location="SEOEngine.validate_seo_package",
                    suggested_fix="config/seo_templates.yaml의 축당 제목을 4개 이상 유지하세요.",
                )
            unknown = {c["trigger"] for c in candidates} - set(TRIGGER_AXES)
            if unknown:
                raise ADOSValidationError(
                    f"{key}에 알 수 없는 트리거 축: {sorted(unknown)}",
                    location="SEOEngine.validate_seo_package",
                    suggested_fix="트리거는 5축 중 하나여야 합니다: " + ", ".join(TRIGGER_AXES),
                )
            for axis in TRIGGER_AXES:
                count = sum(1 for c in candidates if c["trigger"] == axis)
                if count < 3:
                    raise ADOSValidationError(
                        f"{key}의 {axis} 축 후보가 3개 미만입니다: {count}개",
                        location="SEOEngine.validate_seo_package",
                        suggested_fix="config/seo_templates.yaml에서 해당 축을 보강하세요.",
                    )
        ab_sets = package["ab_test_sets"]
        if len(ab_sets) != 3 or any(s["a"]["trigger"] == s["b"]["trigger"] for s in ab_sets):
            raise ADOSValidationError(
                "ab_test_sets는 서로 다른 축끼리 짝지은 3세트여야 합니다.",
                location="SEOEngine.validate_seo_package",
                suggested_fix="create_seo_package를 다시 실행하세요.",
            )
```

- [ ] **Step 4: 통과 확인 + 데모 스크립트 무변경 확인**

Run: `python -m unittest tests.test_scene_script_world_seo -v`
Expected: PASS. (`scripts/run_scene_script_engine_demo.py`는 `len(seo['title_candidates_ko'])`만 사용하므로 dict 목록에서도 그대로 동작 — 수정 불필요.)

- [ ] **Step 5: 커밋**

```bash
git add engines/seo/seo_engine.py tests/test_scene_script_world_seo.py
git commit -m "feat: tag SEO candidates with trigger axes and add deterministic A/B sets"
```

---

### Task 11: 전체 회귀 + 마무리

**Files:**
- Modify: 없음 (검증만; 실패 시 해당 태스크로 돌아가 수정)

- [ ] **Step 1: 전체 테스트**

Run: `python -m unittest discover -s tests -p "test_*.py"`
Expected: OK — 기존 249개 + 신규 약 29개 전부 통과, FAIL/ERROR 0.

- [ ] **Step 2: 데모 스크립트 회귀 (SEO 소비처)**

Run: `python scripts/run_scene_script_engine_demo.py`
Expected: 종전과 같이 `title_candidates : ko 20 / en 20` 출력, 에러 없음.

- [ ] **Step 3: 마무리 커밋 (잔여 변경이 있을 때만)**

```bash
git status
```

이 계획의 파일 외 변경이 없어야 정상. 있다면 원인 확인 후 처리.
