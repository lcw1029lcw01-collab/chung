# -*- coding: utf-8 -*-
"""나레이션 생성 — Typecast 신형 API로 블록별 wav를 만든다.

임시 TTS(edge-tts)를 실제 채널 목소리(Typecast)로 교체한다.
블록 텍스트는 워크스페이스의 narration_blocks.json에서 읽는다:
  {"blocks": [{"id": "NB001", "text": "..."}, ...]}
채널 보이스는 channels/{channel_id}/narration_profile.yaml에서 읽는다
(--voice 로 특정 voice_id 강제 지정 가능).

출력: {workspace}/audio/{block_id}.wav (44.1kHz mono)
      각 블록의 실측 길이를 stdout에 출력 (빌드 타이밍 재계산용)

실행: 프로젝트 루트에서
  python scripts/generate_narration.py {workspace} {channel_id} [--voice tc_xxx] [--emotion normal]
"""
import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import load_yaml  # noqa: E402
from providers.typecast_provider import TypecastProvider  # noqa: E402


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("channel_id")
    ap.add_argument("--voice", default=None, help="voice_id 강제 지정")
    ap.add_argument("--emotion", default=None)
    args = ap.parse_args()

    workspace = Path(args.workspace)
    blocks_path = workspace / "narration_blocks.json"
    if not blocks_path.is_file():
        print(f"narration_blocks.json이 없습니다: {blocks_path}")
        return 1
    import json
    blocks = json.loads(blocks_path.read_text(encoding="utf-8"))["blocks"]

    profile_path = PROJECT_ROOT / "channels" / args.channel_id / "narration_profile.yaml"
    profile = load_yaml(profile_path) if profile_path.is_file() else {}
    tc = profile.get("typecast", {})
    voice_id = args.voice or tc.get("voice_id")
    emotion = args.emotion or tc.get("emotion", "normal")
    model = tc.get("model", "ssfm-v30")
    if not voice_id:
        print("voice_id가 없습니다 — narration_profile.yaml 또는 --voice로 지정하세요.")
        return 1

    provider = TypecastProvider()
    audio_dir = workspace / "audio"
    print(f"voice_id: {voice_id} | emotion: {emotion} | model: {model}")
    total = 0.0
    for block in blocks:
        dest = audio_dir / f"{block['id']}.wav"
        provider.synthesize(block["text"], voice_id, dest, emotion=emotion, model=model)
        dur = probe_duration(dest)
        total += dur
        print(f"  {block['id']}: {dur:.2f}s  {block['text'][:40]}")
    print(f"[완료] {len(blocks)}블록, 나레이션 합계 {total:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
