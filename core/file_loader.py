# -*- coding: utf-8 -*-
"""ADOS file I/O helpers.

모든 파일은 UTF-8. JSON/YAML key는 snake_case (docs/02_DEVELOPMENT_RULES.md #7.4).
"""
import json
from pathlib import Path

from .errors import ADOSConfigError, ADOSFileNotFoundError

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

_YAML_MISSING_MSG = (
    "PyYAML이 설치되어 있지 않아 YAML을 처리할 수 없습니다. "
    "'pip install pyyaml'로 설치하세요."
)


def file_exists(path: str | Path) -> bool:
    return Path(path).is_file()


def ensure_directory(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _require_file(path: str | Path, location: str) -> Path:
    p = Path(path)
    if not p.is_file():
        raise ADOSFileNotFoundError(
            f"파일이 없습니다: {p}",
            location=location,
            suggested_fix="경로를 확인하거나 파일을 먼저 생성하세요.",
        )
    return p


def load_text(path: str | Path) -> str:
    p = _require_file(path, "file_loader.load_text")
    return p.read_text(encoding="utf-8")


def write_text(path: str | Path, text: str) -> Path:
    p = Path(path)
    ensure_directory(p.parent)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def load_json(path: str | Path) -> dict | list:
    p = _require_file(path, "file_loader.load_json")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ADOSConfigError(
            f"JSON 파싱 실패: {p}",
            location="file_loader.load_json",
            cause=str(e),
            suggested_fix="JSON 문법을 확인하세요.",
        ) from e


def write_json(path: str | Path, data: dict | list) -> Path:
    p = Path(path)
    ensure_directory(p.parent)
    p.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return p


def load_yaml(path: str | Path) -> dict | list:
    if yaml is None:
        raise ADOSConfigError(_YAML_MISSING_MSG, location="file_loader.load_yaml")
    p = _require_file(path, "file_loader.load_yaml")
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ADOSConfigError(
            f"YAML 파싱 실패: {p}",
            location="file_loader.load_yaml",
            cause=str(e),
            suggested_fix="YAML 문법을 확인하세요.",
        ) from e


def write_yaml(path: str | Path, data: dict | list) -> Path:
    if yaml is None:
        raise ADOSConfigError(_YAML_MISSING_MSG, location="file_loader.write_yaml")
    p = Path(path)
    ensure_directory(p.parent)
    p.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    return p
