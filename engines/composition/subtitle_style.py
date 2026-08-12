# -*- coding: utf-8 -*-
"""자막 스타일 — 채널 프리셋을 해석하고 ASS 자막 파일 텍스트를 생성한다.

SRT + force_style 대신 .ass를 직접 만든다. 이유: subtitles 필터가 SRT를 ASS로
변환할 때 기본 해상도(384x288)로 스케일해 폰트가 뻥튀기되던 문제를 원천 차단하고,
PlayRes(1920x1080)와 스타일을 우리가 완전히 통제하기 위해서다.
근거: docs/superpowers/specs/2026-07-12-longform-subtitle-system-design.md

순수 함수 + yaml 로드만 둔다 — ffmpeg 실행은 VideoComposer가 담당.
"""
from pathlib import Path

from core import ADOSConfigError, load_yaml

# [Script Info] 기본값 — 프리셋에서 덮어쓸 수 있다.
_SCRIPT_INFO_DEFAULTS = {
    "PlayResX": 1920,
    "PlayResY": 1080,
    "WrapStyle": 0,
    "ScaledBorderAndShadow": "yes",
}

# [V4+ Styles] Style: 라인의 필드 순서와 기본값.
# 프리셋은 이 키들을 부분적으로 덮어쓴다.
_STYLE_FIELD_DEFAULTS = {
    "FontName": "Malgun Gothic",
    "Fontsize": 50,
    "PrimaryColour": "&H00FFFFFF",
    "SecondaryColour": "&H000000FF",
    "OutlineColour": "&H00000000",
    "BackColour": "&H00000000",
    "Bold": 1,
    "Italic": 0,
    "Underline": 0,
    "StrikeOut": 0,
    "ScaleX": 100,
    "ScaleY": 100,
    "Spacing": 0,
    "Angle": 0,
    "BorderStyle": 1,
    "Outline": 2.4,
    "Shadow": 1.2,
    "Alignment": 2,
    "MarginL": 160,
    "MarginR": 160,
    "MarginV": 70,
    "Encoding": 1,
}

_STYLE_FIELD_ORDER = [
    "Name", "FontName", "Fontsize", "PrimaryColour", "SecondaryColour",
    "OutlineColour", "BackColour", "Bold", "Italic", "Underline", "StrikeOut",
    "ScaleX", "ScaleY", "Spacing", "Angle", "BorderStyle", "Outline", "Shadow",
    "Alignment", "MarginL", "MarginR", "MarginV", "Encoding",
]

_EVENTS_FORMAT = (
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
    "Effect, Text"
)


def load_styles(path: str | Path) -> dict:
    """config/subtitle_styles.yaml을 로드한다 (최상위 dict: default + presets)."""
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise ADOSConfigError(
            f"자막 스타일 파일의 최상위는 dict여야 합니다: {path}",
            location="subtitle_style.load_styles",
        )
    return data


def resolve_style(
    styles: dict, preset_name: str, overrides: dict | None = None
) -> dict:
    """스타일을 해석한다: default ← preset ← overrides 순으로 병합."""
    presets = styles.get("presets", {})
    if preset_name not in presets:
        raise ADOSConfigError(
            f"정의되지 않은 자막 프리셋: {preset_name}",
            location="subtitle_style.resolve_style",
            suggested_fix=f"config/subtitle_styles.yaml presets에 '{preset_name}'을 추가하세요.",
        )
    resolved = dict(styles.get("default", {}))
    resolved.update(presets[preset_name])
    if overrides:
        resolved.update(overrides)
    return resolved


def _ass_time(seconds: float) -> str:
    """초 → ASS 시간 문자열 H:MM:SS.cc (센티초)."""
    centis = int(round(max(0.0, seconds) * 100))
    hours, centis = divmod(centis, 360000)
    minutes, centis = divmod(centis, 6000)
    secs, centis = divmod(centis, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def _fmt_num(value) -> str:
    """정수는 정수로, 실수는 불필요한 0을 떼고 문자열화."""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _script_info_block(style: dict) -> str:
    info = dict(_SCRIPT_INFO_DEFAULTS)
    for key in _SCRIPT_INFO_DEFAULTS:
        if key in style:
            info[key] = style[key]
    lines = ["[Script Info]", "ScriptType: v4.00+"]
    lines += [f"{key}: {_fmt_num(info[key])}" for key in _SCRIPT_INFO_DEFAULTS]
    return "\n".join(lines)


def _styles_block(style: dict) -> str:
    fields = dict(_STYLE_FIELD_DEFAULTS)
    for key in _STYLE_FIELD_DEFAULTS:
        if key in style:
            fields[key] = style[key]
    fields["Name"] = "Default"
    values = [_fmt_num(fields[key]) for key in _STYLE_FIELD_ORDER]
    format_line = "Format: " + ", ".join(_STYLE_FIELD_ORDER)
    return "\n".join(["[V4+ Styles]", format_line, "Style: " + ",".join(values)])


def _events_block(cues: list[dict]) -> str:
    lines = ["[Events]", _EVENTS_FORMAT]
    for cue in cues:
        cue_lines = cue.get("lines") or [cue.get("text", "")]
        text = r"\N".join(cue_lines)
        start = _ass_time(float(cue["start_seconds"]))
        end = _ass_time(float(cue["end_seconds"]))
        lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
    return "\n".join(lines)


def build_ass(cues: list[dict], style: dict) -> str:
    """리플로우된 큐 + 해석된 스타일로 완성된 .ass 텍스트를 만든다."""
    return "\n\n".join(
        [_script_info_block(style), _styles_block(style), _events_block(cues)]
    ) + "\n"
