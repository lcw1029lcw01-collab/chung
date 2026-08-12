# -*- coding: utf-8 -*-
"""자막 리플로우 — 나레이션 큐(문장 통째)를 표시 최적화 큐로 재가공한다.

넷플릭스 한국어 자막 기준: 줄당 ≤16자(한글 1자, 영문/공백/문장부호 0.5자),
최대 2줄, 의미(단어) 경계에서만 줄바꿈, 2줄 초과분은 시간대를 나눠 여러 큐로.
근거: docs/superpowers/specs/2026-07-12-longform-subtitle-system-design.md

순수 함수만 둔다 — ffmpeg/파일 IO 없음.
"""
import re
import unicodedata

# 단어 사이 공백의 표시 폭 (한글 1.0, 영문/부호 0.5 규칙과 동일하게 공백=0.5)
_SPACE_WIDTH = 0.5

# 문장 경계 — 마침표/물음표/느낌표(반각·전각) 뒤 공백에서 나눈다.
_SENTENCE_SPLIT = re.compile(r"(?<=[.?!。？！])\s+")


def _split_sentences(text: str) -> list[str]:
    """텍스트를 문장 단위로 나눈다(문장부호는 문장에 남긴다)."""
    return [p.strip() for p in _SENTENCE_SPLIT.split(text.strip()) if p.strip()]


def char_width(text: str) -> float:
    """자막 표시 폭을 잰다. 넷플릭스 규칙: 전각(한글·한자) 1.0, 그 외 0.5."""
    total = 0.0
    for ch in text:
        total += 1.0 if unicodedata.east_asian_width(ch) in ("W", "F") else 0.5
    return total


def _hard_split_word(word: str, max_width: float) -> list[str]:
    """공백이 없어 한 단어가 한 줄을 넘길 때, 글자 단위로 부득이 나눈다."""
    pieces = []
    cur = ""
    for ch in word:
        if char_width(cur + ch) > max_width and cur:
            pieces.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        pieces.append(cur)
    return pieces


def _wrap_words(text: str, max_width: float) -> list[str]:
    """단어(어절) 경계로만 줄을 나눈다. 단어 중간 분할 없음(초장 단어만 예외)."""
    words = []
    for raw in text.split():
        if char_width(raw) > max_width:
            words.extend(_hard_split_word(raw, max_width))
        else:
            words.append(raw)

    lines: list[str] = []
    cur: list[str] = []
    cur_w = 0.0
    for word in words:
        ww = char_width(word)
        if not cur:
            cur, cur_w = [word], ww
            continue
        new_w = cur_w + _SPACE_WIDTH + ww
        if new_w <= max_width:
            cur.append(word)
            cur_w = new_w
        else:
            lines.append(" ".join(cur))
            cur, cur_w = [word], ww
    if cur:
        lines.append(" ".join(cur))
    return lines


def _balance_two_lines(lines: list[str], max_width: float) -> list[str]:
    """딱 2줄일 때 아래쪽을 길게(역피라미드) 재배치한다 — 넷플릭스 권장.

    두 줄의 전체 단어를 이어붙인 뒤, 위 줄이 아래 줄보다 짧아지도록 분할점을
    고르되 두 줄 모두 max_width를 넘지 않게 한다.
    """
    words = " ".join(lines).split()
    if len(words) < 2:
        return lines
    best = None  # (top_heavy_penalty, max_line_width, [top, bottom])
    for split in range(1, len(words)):
        top = " ".join(words[:split])
        bottom = " ".join(words[split:])
        tw, bw = char_width(top), char_width(bottom)
        if tw > max_width or bw > max_width:
            continue
        # 위 줄이 아래 줄보다 길면 감점(역피라미드 위배), 폭 균형도 고려
        top_heavy_penalty = max(0.0, tw - bw)
        key = (top_heavy_penalty, abs(tw - bw))
        if best is None or key < best[0]:
            best = (key, [top, bottom])
    return best[1] if best else lines


def _append_groups(out: list[dict], cue: dict, groups: list[list[str]]) -> None:
    """줄 그룹(각 그룹 = 한 큐의 줄들)에 원래 큐의 시간대를 글자수 비례로 배분."""
    start = float(cue["start_seconds"])
    end = float(cue["end_seconds"])
    span = max(0.0, end - start)
    weights = [sum(char_width(line) for line in group) or 1.0 for group in groups]
    total = sum(weights)
    t = start
    for i, group in enumerate(groups):
        seg_end = end if i == len(groups) - 1 else t + span * (weights[i] / total)
        out.append(
            {
                "start_seconds": t,
                "end_seconds": seg_end,
                "lines": list(group),
                "text": "\n".join(group),
            }
        )
        t = seg_end


def reflow_cues(
    cues: list[dict], max_chars_per_line: float = 16, max_lines: int = 2
) -> list[dict]:
    """나레이션 큐 목록을 표시 최적화 큐 목록으로 변환한다.

    문장 경계를 먼저 나눠 문장을 절대 섞지 않는다(각 표시 큐는 한 문장으로 끝난다).
    긴 문장만 2줄/여러 큐로 쪼갠다. 각 출력 큐에 lines와 text("\\n" 결합)를 채우고
    index를 재부여한다. 시간은 그룹별 글자수에 비례해 원 큐 시간대를 배분한다.
    """
    out: list[dict] = []
    for cue in cues:
        text = str(cue["text"]).strip()
        sentences = _split_sentences(text) or [text]
        groups: list[list[str]] = []
        for sentence in sentences:
            lines = _wrap_words(sentence, max_chars_per_line)
            if not lines:
                continue
            if len(lines) <= max_lines:
                sub = [lines]
            else:
                sub = [
                    lines[i:i + max_lines] for i in range(0, len(lines), max_lines)
                ]
            # 정확히 2줄인 그룹은 역피라미드로 균형
            if max_lines == 2:
                sub = [
                    _balance_two_lines(g, max_chars_per_line) if len(g) == 2 else g
                    for g in sub
                ]
            groups.extend(sub)
        if not groups:
            continue
        _append_groups(out, cue, groups)
    for i, cue in enumerate(out, 1):
        cue["index"] = i
    return out


def reading_speed_warnings(cues: list[dict], max_cps: float = 12) -> list[dict]:
    """읽기 속도(초당 표시 폭)가 상한을 넘는 큐를 리포트한다(강제 수정 X)."""
    warnings = []
    for cue in cues:
        duration = float(cue["end_seconds"]) - float(cue["start_seconds"])
        load = char_width(str(cue.get("text", "")).replace("\n", " "))
        if duration > 0 and load / duration > max_cps:
            warnings.append(
                {
                    "cue_index": cue["index"],
                    "cps": round(load / duration, 2),
                    "text": cue.get("text", ""),
                }
            )
    return warnings
