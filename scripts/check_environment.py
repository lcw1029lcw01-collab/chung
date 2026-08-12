# -*- coding: utf-8 -*-
"""실행 환경 점검 — 필수/선택 의존성을 검사하고 설치 안내를 출력한다.

필수 항목이 하나라도 없으면 non-zero exit code를 반환한다.
자동 설치는 하지 않는다.

실행: python scripts/check_environment.py
"""
import importlib.util
import io
import shutil
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MIN_PYTHON = (3, 11)  # StrEnum, zoneinfo 등 사용

REQUIRED_MODULES = [
    ("yaml", "PyYAML", "pip install PyYAML"),
    ("requests", "requests", "pip install requests"),
]

OPTIONAL_MODULES = [
    ("playwright", "playwright (미드저니 CDP 브리지용)", "pip install playwright"),
]

REQUIRED_BINARIES = [
    ("ffmpeg", "영상 합성/자막 번인", "winget install Gyan.FFmpeg 또는 https://ffmpeg.org"),
    ("ffprobe", "미디어 길이/스트림 측정", "ffmpeg 패키지에 포함"),
]

OPTIONAL_BINARIES = [
    ("yt-dlp", "경쟁 채널 스캐너용", "pip install yt-dlp"),
]


def check_python() -> bool:
    ok = sys.version_info >= MIN_PYTHON
    version = ".".join(map(str, sys.version_info[:3]))
    mark = "OK " if ok else "없음"
    print(f"[{mark}] Python >= {'.'.join(map(str, MIN_PYTHON))}  (현재 {version})")
    if not ok:
        print(f"      → Python {'.'.join(map(str, MIN_PYTHON))} 이상을 설치하세요: https://www.python.org")
    return ok


def check_module(module: str, label: str, fix: str, required: bool) -> bool:
    found = importlib.util.find_spec(module) is not None
    mark = "OK " if found else ("없음" if required else "선택")
    print(f"[{mark}] {label}")
    if not found:
        print(f"      → {fix}")
    return found or not required


def check_binary(binary: str, label: str, fix: str, required: bool) -> bool:
    found = shutil.which(binary) is not None
    mark = "OK " if found else ("없음" if required else "선택")
    print(f"[{mark}] {binary} — {label}")
    if not found:
        print(f"      → {fix}")
    return found or not required


def main() -> int:
    print("=== ADOS 환경 점검 ===")
    ok = check_python()
    print()
    print("Python 패키지 (필수):")
    for module, label, fix in REQUIRED_MODULES:
        ok = check_module(module, label, fix, required=True) and ok
    print()
    print("Python 패키지 (선택):")
    for module, label, fix in OPTIONAL_MODULES:
        check_module(module, label, fix, required=False)
    print()
    print("실행 파일 (필수):")
    for binary, label, fix in REQUIRED_BINARIES:
        ok = check_binary(binary, label, fix, required=True) and ok
    print()
    print("실행 파일 (선택):")
    for binary, label, fix in OPTIONAL_BINARIES:
        check_binary(binary, label, fix, required=False)
    print()
    if ok:
        print("결과: 필수 항목 모두 충족")
        return 0
    print("결과: 필수 항목 누락 — 위 안내에 따라 설치 후 다시 실행하세요")
    return 1


if __name__ == "__main__":
    sys.exit(main())
