# -*- coding: utf-8 -*-
"""SEO engine (publishing layer v1).

에피소드의 업로드 메타데이터 후보를 만든다 — 한/영 제목 20개씩,
설명(챕터 타임스탬프 포함), 태그, 썸네일 문구, 고정 댓글.
근거: docs/37_SCENE_SCRIPT_AND_WORLD_ENGINE_V1.md #5

주의: 결정적 공식(템플릿) 기반이다. LLM을 호출하지 않는다.
실제 업로드는 하지 않는다 — 후보 생성까지만.
"""
from datetime import datetime, timezone
from pathlib import Path

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

PACKAGE_DIR = "package"
SEO_PACKAGE_FILE = "seo_package.json"
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


SEO_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "title_candidates_ko",
    "title_candidates_en",
    "description",
    "tags",
    "chapters",
    "thumbnail_text_candidates",
    "pinned_comment",
    "ab_test_sets",
    "created_at",
]

BASE_TAGS = [
    "미래", "다큐멘터리", "과학", "인류의 미래", "진화", "미래 기술",
    "future", "documentary", "science", "future of humanity", "evolution", "ai",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _format_timestamp(seconds: float) -> str:
    total = int(seconds)
    minutes, secs = divmod(total, 60)
    return f"{minutes:02d}:{secs:02d}"


class SEOEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def package_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / PACKAGE_DIR / SEO_PACKAGE_FILE

    @staticmethod
    def _build_chapters(project_path: Path) -> list[dict]:
        """장면 대본(있으면)에서 구간별 챕터 타임스탬프를 만든다."""
        script_path = project_path / "story" / "scene_script.json"
        if not script_path.is_file():
            return [{"timestamp": "00:00", "title": "인트로"}]
        script = load_json(script_path)
        chapters = []
        cursor = 0.0
        seen_sections: set[str] = set()
        section_titles = {
            "hook": "인트로",
            "setup": "변화의 시작",
            "development": "세 가지 방향",
            "payoff": "갈라지는 인류",
            "ending": "변하지 않는 것들",
        }
        for scene in script["scenes"]:
            section = scene["section"]
            if section not in seen_sections:
                seen_sections.add(section)
                chapters.append(
                    {
                        "timestamp": _format_timestamp(cursor),
                        "title": section_titles.get(section, section),
                    }
                )
            cursor += float(scene["duration_seconds"])
        return chapters

    def create_seo_package(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project_json = project_path / "project.json"
        if not project_json.is_file():
            raise ADOSFileNotFoundError(
                f"project.json이 없습니다: {project_json}",
                location="SEOEngine.create_seo_package",
                suggested_fix="ProjectEngine.create_project를 먼저 실행하세요.",
            )
        project = load_json(project_json)
        topic_json = project_path / "topic.json"
        topic_data = load_json(topic_json) if topic_json.is_file() else {}
        topic = project["topic"]["title"]
        topic_en = topic_data.get("slug", "the-future-of-humanity").replace("-", " ").title()

        # 세계관 앵커 연도 (scene_script가 있으면 거기서)
        year = 1000000
        script_path = project_path / "story" / "scene_script.json"
        if script_path.is_file():
            anchor = load_json(script_path).get("world_anchor")
            if anchor:
                year = anchor["year"]

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

        chapters = self._build_chapters(project_path)
        chapter_lines = "\n".join(f"{chapter['timestamp']} {chapter['title']}" for chapter in chapters)
        description = (
            f"{topic}\n\n"
            f"과학이 예측하는 인류의 미래를 넷플릭스급 다큐멘터리로 담았습니다.\n"
            f"이 채널의 모든 에피소드는 하나의 연속된 미래 역사를 공유합니다.\n\n"
            f"[챕터]\n{chapter_lines}\n\n"
            f"#미래 #다큐멘터리 #과학"
        )
        keywords = [word for word in topic_data.get("keywords", []) if word]
        tags = list(dict.fromkeys(BASE_TAGS + keywords))[:20]

        package = {
            "project_id": project["project_id"],
            "topic": topic,
            "seo_mode": "formula_v2_triggers",
            "title_candidates_ko": title_candidates_ko,
            "title_candidates_en": title_candidates_en,
            "description": description,
            "tags": tags,
            "chapters": chapters,
            "thumbnail_text_candidates": thumbnail_candidates,
            "pinned_comment": (
                "여러분은 100만 년 후 인간이 어떤 모습일 거라고 생각하시나요? "
                "댓글로 여러분의 상상을 들려주세요. 다음 에피소드의 소재가 될 수 있습니다."
            ),
            "ab_test_sets": _build_ab_test_sets(title_candidates_ko),
            "upload_notes": [
                "제목은 후보 중 사람이 최종 선택한다 (A/B 테스트 권장)",
                "AI 생성 콘텐츠 표시는 업로드 시 수동으로 체크한다",
            ],
            "created_at": _now_iso(),
        }
        write_json(self.package_path(project_path), package)
        if self.logger:
            self.logger.info(
                f"SEO 패키지 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return package

    def load_seo_package(self, project_path: str | Path) -> dict:
        path = self.package_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"seo_package.json이 없습니다: {path}",
                location="SEOEngine.load_seo_package",
                suggested_fix="create_seo_package를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_seo_package(self, project_path: str | Path) -> bool:
        package = self.load_seo_package(project_path)
        ADOSValidator.require_fields(
            package, SEO_REQUIRED_FIELDS, location="SEOEngine.validate_seo_package"
        )
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
        if len(package["tags"]) < 10:
            raise ADOSValidationError(
                f"태그가 10개 미만입니다: {len(package['tags'])}개",
                location="SEOEngine.validate_seo_package",
                suggested_fix="기본 태그 + 토픽 키워드를 확인하세요.",
            )
        if not package["chapters"]:
            raise ADOSValidationError(
                "챕터가 비어 있습니다.",
                location="SEOEngine.validate_seo_package",
                suggested_fix="scene_script 생성 후 다시 실행하세요.",
            )
        return True
