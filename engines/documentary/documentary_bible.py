# -*- coding: utf-8 -*-
"""Documentary bible engine (direction layer v1).

채널 단위의 다큐멘터리 연출 바이블을 만든다 — 비주얼 모티프, 컬러/카메라/
캐릭터 바이블, 금지 패턴, 나레이션·음악·편집 리듬 규칙.
전체 원칙: docs/35_AI_DOCUMENTARY_ENGINE_V1.md

주의: 실제 미디어를 생성하지 않는다. 외부 API를 호출하지 않는다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSValidationError,
    ADOSValidator,
    load_yaml,
    write_yaml,
)

BIBLE_FILE = "documentary_bible.yaml"

BIBLE_REQUIRED_FIELDS = [
    "channel_id",
    "channel_name",
    "visual_motifs",
    "recurring_opening_motif",
    "color_bible",
    "camera_bible",
    "character_bible",
    "forbidden_visual_patterns",
    "narration_style",
    "music_style",
    "editing_rhythm",
    "created_at",
]

# 카메라 바이블 — 샷 다양성의 원천 (docs/35 #7 Shot Variety)
CAMERA_BIBLE = {
    "ultra_wide_establishing": {"lens": "24mm", "movement": "slow_dolly_in", "usage": "도시·행성·공간 전체를 여는 샷"},
    "close_up": {"lens": "85mm", "movement": "static", "usage": "감정·표정·디테일 집중"},
    "extreme_close_up": {"lens": "100mm_macro", "movement": "static", "usage": "눈·손·질감의 극단적 몰입"},
    "drone_orbit": {"lens": "35mm", "movement": "orbit", "usage": "규모감과 클라이맥스 임팩트"},
    "over_the_shoulder": {"lens": "50mm", "movement": "handheld_drift", "usage": "인물 시점의 공간 관찰"},
    "side_profile": {"lens": "50mm", "movement": "slow_pan", "usage": "인물 실루엣과 이동 묘사"},
    "pov": {"lens": "28mm", "movement": "walking", "usage": "1인칭 몰입 전환"},
    "low_angle": {"lens": "35mm", "movement": "slow_tilt_up", "usage": "위압감·경외감 연출"},
    "high_angle": {"lens": "35mm", "movement": "slow_crane_down", "usage": "조망·관찰자 시점"},
    "macro_detail": {"lens": "100mm_macro", "movement": "rack_focus", "usage": "사물 표면·소재의 미시 묘사"},
    "handheld_tracking": {"lens": "35mm", "movement": "tracking", "usage": "움직임을 따라가는 생동감"},
}

# 컬러 바이블 — 세계관별 색 언어 (docs/35 #8 Color Bible)
COLOR_BIBLE = {
    "earth": "blue",
    "mars": "orange",
    "moon": "gray",
    "future": "cyan",
    "danger": "red",
    "memory": "warm",
    "master_grade": "cyan_orange_dark",
}

VISUAL_MOTIFS = [
    "earth_hologram",
    "hud_year_display",
    "simulation_start_opening",
    "cyan_orange_grade",
    "atmosphere_particles",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DocumentaryBibleEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def bible_path(self, channel_path: str | Path) -> Path:
        return Path(channel_path) / BIBLE_FILE

    def create_channel_documentary_bible(self, channel_path: str | Path) -> dict:
        channel_path = Path(channel_path)
        channel_yaml = channel_path / "channel.yaml"
        if not channel_yaml.is_file():
            raise ADOSFileNotFoundError(
                f"channel.yaml이 없습니다: {channel_yaml}",
                location="DocumentaryBibleEngine.create_channel_documentary_bible",
                suggested_fix="ChannelEngine.create_channel로 채널을 먼저 만드세요.",
            )
        path = self.bible_path(channel_path)
        if path.is_file():
            raise ADOSValidationError(
                f"documentary_bible.yaml이 이미 존재합니다: {path}",
                location="DocumentaryBibleEngine.create_channel_documentary_bible",
                suggested_fix="기존 바이블을 유지하려면 load를, 재생성하려면 파일을 직접 삭제 후 실행하세요.",
            )
        channel = load_yaml(channel_yaml)

        bible = {
            "channel_id": channel["channel_id"],
            "channel_name": channel["channel_name"],
            "style": "netflix_future_documentary",
            "visual_motifs": list(VISUAL_MOTIFS),
            "recurring_opening_motif": {
                "name": "simulation_start_opening",
                "description": "매 에피소드 동일한 오프닝 — 지구 홀로그램 위 HUD 연도 표시가 미래로 가속",
                "duration_seconds": 4,
            },
            "color_bible": dict(COLOR_BIBLE),
            "camera_bible": {name: dict(spec) for name, spec in CAMERA_BIBLE.items()},
            "character_bible": {
                "future_human_type_a": {
                    "height_cm": 190,
                    "skin": "transparent bio skin",
                    "eyes": "no visible pupils",
                    "hair": "none",
                    "suit": "nano fabric",
                    "emotion": "calm",
                    "walking_style": "slow confident",
                },
            },
            "forbidden_visual_patterns": [
                "같은 카메라 타입을 3샷 연속 반복",
                "인물 뒷모습 와이드 샷의 반복 나열",
                "프레임 안에 읽을 수 있는 텍스트 (간판/화면/책/번호판)",
                "5초를 넘는 연속 AI 영상",
                "모든 샷이 같은 피사체(인물)만 반복",
            ],
            "narration_style": {
                "voice_mood": "calm confident narrator",
                "speed": "medium_slow",
                "language": channel.get("language", "ko"),
            },
            "music_style": {
                "theme": "ambient orchestral hybrid",
                "recurring_theme": True,
            },
            "editing_rhythm": {
                "scene_change_seconds_min": 2,
                "scene_change_seconds_max": 10,
                "principle": "사람은 영상이 아니라 장면 전환(Scene Change)을 본다",
            },
            "created_at": _now_iso(),
        }
        write_yaml(path, bible)
        if self.logger:
            self.logger.info(
                f"다큐멘터리 바이블 생성: {channel['channel_id']}",
                metadata={"channel_id": channel["channel_id"]},
            )
        return bible

    def load_channel_documentary_bible(self, channel_path: str | Path) -> dict:
        path = self.bible_path(channel_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"documentary_bible.yaml이 없습니다: {path}",
                location="DocumentaryBibleEngine.load_channel_documentary_bible",
                suggested_fix="create_channel_documentary_bible을 먼저 실행하세요.",
            )
        return load_yaml(path)

    def validate_channel_documentary_bible(self, channel_path: str | Path) -> bool:
        bible = self.load_channel_documentary_bible(channel_path)
        ADOSValidator.require_fields(
            bible,
            BIBLE_REQUIRED_FIELDS,
            location="DocumentaryBibleEngine.validate_channel_documentary_bible",
        )
        if len(bible["camera_bible"]) < 8:
            raise ADOSValidationError(
                f"camera_bible 종류가 부족합니다: {len(bible['camera_bible'])}개 (최소 8개)",
                location="DocumentaryBibleEngine.validate_channel_documentary_bible",
                suggested_fix="샷 다양성을 위해 카메라 타입을 8개 이상 정의하세요.",
            )
        return True
