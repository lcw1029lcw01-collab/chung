# -*- coding: utf-8 -*-
"""샘플 채널 생성 스크립트 (walking skeleton).

실행: 프로젝트 루트에서  python scripts/create_sample_channel.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSPathManager  # noqa: E402
from engines.channel import ChannelEngine  # noqa: E402

SAMPLE_CHANNEL_REQUEST = {
    "channel_id": "future",
    "channel_name": "Future Lab",
    "template_id": "future_documentary_template",
    "language": "ko",
}


def channel_exists(path_manager: ADOSPathManager) -> bool:
    channel_id = SAMPLE_CHANNEL_REQUEST["channel_id"]
    return (path_manager.channels / channel_id / "channel.yaml").is_file()


def create_sample_channel(path_manager: ADOSPathManager | None = None) -> dict:
    pm = path_manager or ADOSPathManager()
    return ChannelEngine(pm).create_channel(dict(SAMPLE_CHANNEL_REQUEST))


def main() -> int:
    pm = ADOSPathManager()
    if channel_exists(pm):
        path = pm.channels / SAMPLE_CHANNEL_REQUEST["channel_id"]
        print(f"채널이 이미 존재합니다: {path}")
        print("새로 만들려면 해당 폴더를 정리한 뒤 다시 실행하세요.")
        return 0
    result = create_sample_channel(pm)
    print(f"채널 생성 완료: {result['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
