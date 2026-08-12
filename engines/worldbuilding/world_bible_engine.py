# -*- coding: utf-8 -*-
"""World bible engine (worldbuilding layer v1).

채널 단위의 세계관 바이블을 만든다 — 시청자는 영상 하나가 아니라
"하나의 연속된 미래 역사"를 따라간다. 모든 에피소드는 같은 우주를
공유하고, 연표(timeline)의 한 지점에 앵커된다.
근거: docs/37_SCENE_SCRIPT_AND_WORLD_ENGINE_V1.md #3

주의: 실제 미디어를 생성하지 않는다. 외부 API를 호출하지 않는다.
기본 연표는 placeholder다 — 실제 세계관 설계는 사람/CTO가 채운다.
"""
import re
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

WORLD_BIBLE_FILE = "world_bible.yaml"
CONTINUITY_FILE = "world_continuity.yaml"

WORLD_BIBLE_REQUIRED_FIELDS = [
    "channel_id",
    "universe_name",
    "timeline",
    "continuity_rules",
    "created_at",
]

TIMELINE_ENTRY_REQUIRED_FIELDS = [
    "year",
    "event",
    "technology",
    "politics",
    "economy",
    "cities",
    "human_form",
    "ai_role",
]

# 기본 연표 (placeholder) — "연속된 미래 역사"의 뼈대
DEFAULT_TIMELINE = [
    {
        "year": 2050,
        "event": "AI가 대부분의 사무직을 대체한다",
        "technology": "범용 업무 AI, 자율 물류",
        "politics": "기본소득 실험 확산",
        "economy": "노동 시장 대전환",
        "cities": "재택·자동화 혼합 도시",
        "human_form": "현생 인류와 동일",
        "ai_role": "도구에서 동료로",
    },
    {
        "year": 2068,
        "event": "최초의 AI 정부 부처가 등장한다",
        "technology": "정책 시뮬레이션 AI",
        "politics": "AI 거버넌스 논쟁",
        "economy": "알고리즘 재정 운영",
        "cities": "센서 통합 스마트시티",
        "human_form": "웨어러블 보조 일반화",
        "ai_role": "행정의 실질 운영자",
    },
    {
        "year": 2080,
        "event": "달 식민지가 상설화된다",
        "technology": "달 기지 자급 체계, 궤도 엘리베이터 초기",
        "politics": "지구-달 이원 행정",
        "economy": "우주 자원 채굴 산업",
        "cities": "달 표면 거주 돔",
        "human_form": "저중력 적응 훈련 세대",
        "ai_role": "우주 인프라의 조종자",
    },
    {
        "year": 2095,
        "event": "인간과 AI의 시민권 논쟁이 시작된다",
        "technology": "자기개선 AI, 뇌-기계 접속 초기",
        "politics": "AI 권리 운동",
        "economy": "인간-AI 혼성 기업",
        "cities": "수직 도시, 해상 도시",
        "human_form": "신경 임플란트 초기 세대",
        "ai_role": "법적 지위를 요구하는 존재",
    },
    {
        "year": 2140,
        "event": "최초의 화성 독립국이 선언된다",
        "technology": "테라포밍 1단계, 저중력 의학",
        "politics": "행성 간 정치의 시작",
        "economy": "행성 간 자원 무역",
        "cities": "화성 돔 도시",
        "human_form": "화성 출생 세대 — 다른 뼈, 다른 심장",
        "ai_role": "행성 인프라의 관리자",
    },
    {
        "year": 2400,
        "event": "지구는 인류의 관광지가 된다",
        "technology": "행성 간 정기 항로",
        "politics": "지구 보존 협약",
        "economy": "귀향 관광 산업",
        "cities": "보존구역이 된 옛 대도시",
        "human_form": "행성별 적응이 시작된 인류",
        "ai_role": "지구 생태 복원의 관리자",
    },
    {
        "year": 3000,
        "event": "지구는 더 이상 인류의 중심이 아니다",
        "technology": "항성계 내 상시 항행",
        "politics": "분산된 인류 연방",
        "economy": "포스트 희소성 경제",
        "cities": "궤도 거주구, 위성 도시",
        "human_form": "환경별 분화가 뚜렷해진 인류",
        "ai_role": "문명의 공동 설계자",
    },
    {
        "year": 1000000,
        "event": "인류는 여러 갈래의 종으로 갈라진다",
        "technology": "유전자 자기 설계",
        "politics": "종을 넘는 연대",
        "economy": "의미 중심 문명",
        "cities": "행성별 고유 문명",
        "human_form": "투명 생체 피부, 확장된 두개, 무모(無毛)",
        "ai_role": "인류와 구분이 무의미해진 동반자",
    },
]

DEFAULT_CONTINUITY_RULES = [
    "모든 에피소드의 연도·사건은 world_bible 연표와 모순되면 안 된다",
    "새로운 사건을 도입하면 연표에 등록한다 (자동 수정 금지, 사람이 승인)",
    "인물·도시·기술의 설정은 한 번 등장하면 유지된다",
    "에피소드는 반드시 연표의 한 지점에 앵커된다 (register_episode_anchor)",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorldBibleEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def bible_path(self, channel_path: str | Path) -> Path:
        return Path(channel_path) / WORLD_BIBLE_FILE

    def continuity_path(self, channel_path: str | Path) -> Path:
        return Path(channel_path) / CONTINUITY_FILE

    def create_channel_world_bible(self, channel_path: str | Path) -> dict:
        channel_path = Path(channel_path)
        channel_yaml = channel_path / "channel.yaml"
        if not channel_yaml.is_file():
            raise ADOSFileNotFoundError(
                f"channel.yaml이 없습니다: {channel_yaml}",
                location="WorldBibleEngine.create_channel_world_bible",
                suggested_fix="ChannelEngine.create_channel로 채널을 먼저 만드세요.",
            )
        path = self.bible_path(channel_path)
        if path.is_file():
            raise ADOSValidationError(
                f"world_bible.yaml이 이미 존재합니다: {path}",
                location="WorldBibleEngine.create_channel_world_bible",
                suggested_fix="기존 세계관을 유지하려면 load를 쓰세요. 세계관은 함부로 재생성하지 않는다.",
            )
        channel = load_yaml(channel_yaml)
        bible = {
            "channel_id": channel["channel_id"],
            "universe_name": f"{channel['channel_name']} Universe (placeholder)",
            "premise": "독립된 에피소드들이 하나의 연속된 미래 역사를 공유한다 (placeholder)",
            "timeline": [dict(entry) for entry in DEFAULT_TIMELINE],
            "continuity_rules": list(DEFAULT_CONTINUITY_RULES),
            "disclaimer": "Placeholder world bible. 실제 세계관 설계로 교체하기 전까지 참고용.",
            "created_at": _now_iso(),
        }
        write_yaml(path, bible)
        if self.logger:
            self.logger.info(
                f"세계관 바이블 생성: {channel['channel_id']}",
                metadata={"channel_id": channel["channel_id"]},
            )
        return bible

    def load_channel_world_bible(self, channel_path: str | Path) -> dict:
        path = self.bible_path(channel_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"world_bible.yaml이 없습니다: {path}",
                location="WorldBibleEngine.load_channel_world_bible",
                suggested_fix="create_channel_world_bible을 먼저 실행하세요.",
            )
        return load_yaml(path)

    def validate_channel_world_bible(self, channel_path: str | Path) -> bool:
        bible = self.load_channel_world_bible(channel_path)
        ADOSValidator.require_fields(
            bible,
            WORLD_BIBLE_REQUIRED_FIELDS,
            location="WorldBibleEngine.validate_channel_world_bible",
        )
        timeline = bible["timeline"]
        if not timeline:
            raise ADOSValidationError(
                "연표가 비어 있습니다 — 세계관에는 최소 1개의 시점이 필요하다.",
                location="WorldBibleEngine.validate_channel_world_bible",
                suggested_fix="timeline에 연도별 사건을 채우세요.",
            )
        years = []
        for entry in timeline:
            ADOSValidator.require_fields(
                entry,
                TIMELINE_ENTRY_REQUIRED_FIELDS,
                location="WorldBibleEngine.validate_channel_world_bible",
            )
            years.append(entry["year"])
        if years != sorted(years):
            raise ADOSValidationError(
                f"연표가 연도 순서가 아닙니다: {years}",
                location="WorldBibleEngine.validate_channel_world_bible",
                suggested_fix="timeline을 연도 오름차순으로 정렬하세요.",
            )
        return True

    # --- 에피소드 연속성 ---
    def resolve_episode_anchor(self, channel_path: str | Path, topic_title: str) -> dict:
        """토픽에 맞는 연표 앵커를 결정적으로 고른다.

        명시적 연도 표현만 인식한다 — "N만 년"(×10000)과 "NNNN년".
        "3가지"·"1000개" 같은 단순 수량이 연도를 하이잭하면 안 된다.
        연도 표현이 없으면 마지막 연표 시점을 쓴다. 여러 개면 가장 먼
        미래(최댓값)를 쓴다 — 미래 다큐의 주제는 보통 가장 먼 시점이다.
        """
        bible = self.load_channel_world_bible(channel_path)
        timeline = bible["timeline"]
        candidates = [
            int(match) * 10000
            for match in re.findall(r"(\d+)\s*만\s*년", topic_title)
        ]
        candidates += [
            int(match) for match in re.findall(r"(\d{3,7})\s*년", topic_title)
        ]
        if candidates:
            target = max(candidates)
            anchor = min(timeline, key=lambda entry: abs(entry["year"] - target))
        else:
            anchor = timeline[-1]
        return dict(anchor)

    def register_episode_anchor(
        self, channel_path: str | Path, project_id: str, year: int, event: str
    ) -> dict:
        """에피소드가 연표의 어느 지점을 다뤘는지 기록한다 (연속성 레지스트리)."""
        channel_path = Path(channel_path)
        self.load_channel_world_bible(channel_path)  # 세계관 없이 등록 금지
        path = self.continuity_path(channel_path)
        continuity = load_yaml(path) if path.is_file() else {"episodes": []}
        episodes = continuity.get("episodes", [])
        if any(episode["project_id"] == project_id for episode in episodes):
            return continuity
        episodes.append(
            {
                "project_id": project_id,
                "year": year,
                "event": event,
                "registered_at": _now_iso(),
            }
        )
        continuity["episodes"] = episodes
        write_yaml(path, continuity)
        if self.logger:
            self.logger.info(
                f"에피소드 앵커 등록: {project_id} → {year}",
                metadata={"project_id": project_id, "year": year},
            )
        return continuity

    def load_continuity(self, channel_path: str | Path) -> dict:
        path = self.continuity_path(channel_path)
        if not path.is_file():
            return {"episodes": []}
        return load_yaml(path)
