# -*- coding: utf-8 -*-
"""Story engine (walking skeleton).

더미 지식을 기반으로 더미 스토리 산출물을 만든다.
전체 스키마는 docs/19_STORY_ENGINE.md 기준으로 이후 확장한다.

장르별 스토리 구조 템플릿(config/story_structures.yaml)을 지원한다 —
"Story Engine만 바꾸면 채널이 바뀐다" (docs/38 #4). 템플릿을 지정하지
않으면 기존 구조(hook/setup/development/payoff/ending)와 동일하다.

주의: 실제 대본 품질 로직은 없다. 모든 출력은 dummy이다.
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

STORY_DIR = "story"
OUTLINE_FILE = "story_outline.json"

OUTLINE_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "story_mode",
    "structure",
    "target_languages",
    "created_at",
]

STRUCTURE_REQUIRED_FIELDS = ["hook", "setup", "development", "payoff", "ending"]

DEFAULT_STRUCTURE_TEMPLATE = "documentary_default"

# config/story_structures.yaml과 동일한 안전 기본값
DEFAULT_STORY_STRUCTURES = {
    "default_template": DEFAULT_STRUCTURE_TEMPLATE,
    "templates": {
        "documentary_default": {
            "description": "기본 다큐 구조",
            "sections": ["hook", "setup", "development", "payoff", "ending"],
        },
    },
}

DUMMY_DISCLAIMER = "Dummy script draft. Not production-ready."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_story_structures(start: str | Path | None = None) -> dict:
    """config/story_structures.yaml을 읽는다. 없으면 기본 템플릿만 쓴다."""
    try:
        root = ADOSPathManager.find_project_root(start)
    except Exception:
        return dict(DEFAULT_STORY_STRUCTURES)
    config_path = root / "config" / "story_structures.yaml"
    if not config_path.is_file():
        return dict(DEFAULT_STORY_STRUCTURES)
    config = load_yaml(config_path)
    if not isinstance(config, dict):
        return dict(DEFAULT_STORY_STRUCTURES)
    templates = dict(DEFAULT_STORY_STRUCTURES["templates"])
    if isinstance(config.get("templates"), dict):
        templates.update(config["templates"])
    return {
        "default_template": config.get(
            "default_template", DEFAULT_STORY_STRUCTURES["default_template"]
        ),
        "templates": templates,
    }


class StoryEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def outline_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / STORY_DIR / OUTLINE_FILE

    def create_dummy_story(
        self, project_path: str | Path, structure_template: str | None = None
    ) -> dict:
        project_path = Path(project_path)
        map_path = project_path / "knowledge" / "knowledge_map.json"
        if not map_path.is_file():
            raise ADOSFileNotFoundError(
                f"knowledge_map.json이 없습니다: {map_path}",
                location="StoryEngine.create_dummy_story",
                suggested_fix="KnowledgeEngine.create_dummy_knowledge를 먼저 실행하세요.",
            )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        knowledge_map = load_json(map_path)

        structures = load_story_structures(project_path)
        template_name = structure_template or structures["default_template"]
        template = structures["templates"].get(template_name)
        if template is None:
            raise ADOSValidationError(
                f"스토리 구조 템플릿이 없습니다: {template_name}",
                location="StoryEngine.create_dummy_story",
                suggested_fix=f"config/story_structures.yaml에 정의된 템플릿을 쓰세요: "
                f"{sorted(structures['templates'])}",
            )

        title = topic["title"]
        if template_name == DEFAULT_STRUCTURE_TEMPLATE:
            structure = {
                "hook": f"'{title}' — 시청자의 호기심을 여는 질문 (placeholder)",
                "setup": f"핵심 개념 소개: {knowledge_map['core_concept']}",
                "development": "지지 포인트들을 순서대로 전개 (placeholder)",
                "payoff": "핵심 질문에 대한 답 제시 (placeholder)",
                "ending": "여운을 남기는 마무리와 다음 영상 예고 (placeholder)",
            }
        else:
            sections = template["sections"]
            structure = {
                sections[0]: f"'{title}' — {sections[0]} 구간 (placeholder)",
                **{
                    section: f"{section} 구간 전개 (placeholder)"
                    for section in sections[1:]
                },
            }
        outline = {
            "project_id": project["project_id"],
            "topic": title,
            "story_mode": "dummy",
            "structure_template": template_name,
            "disclaimer": DUMMY_DISCLAIMER,
            "structure": structure,
            "target_languages": project["languages"]["target_languages"],
            "created_at": _now_iso(),
        }

        duration = int(project["duration"]["target_seconds"])
        narration_blocks = [
            {"block_id": f"NB{i:03d}", "section": section, "text": text}
            for i, (section, text) in enumerate(structure.items(), start=1)
        ]
        script_draft = {
            "project_id": project["project_id"],
            "language": "ko",
            "script_mode": "dummy",
            "title": title,
            "narration_blocks": narration_blocks,
            "estimated_duration_seconds": duration,
            "disclaimer": DUMMY_DISCLAIMER,
            "created_at": _now_iso(),
        }

        folder = project_path / STORY_DIR
        write_json(folder / OUTLINE_FILE, outline)
        write_json(folder / "script_draft.json", script_draft)
        write_json(
            folder / "story_review.json",
            {
                "project_id": project["project_id"],
                "story_mode": "dummy",
                "status": "PENDING_REVIEW",
                "notes": ["더미 스토리 — 실제 품질 검토는 Quality 단계 구현 후 수행."],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 스토리 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return outline

    def load_story_outline(self, project_path: str | Path) -> dict:
        path = self.outline_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"story_outline.json이 없습니다: {path}",
                location="StoryEngine.load_story_outline",
                suggested_fix="create_dummy_story를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_story(self, project_path: str | Path) -> bool:
        outline = self.load_story_outline(project_path)
        ADOSValidator.require_fields(
            outline, OUTLINE_REQUIRED_FIELDS, location="StoryEngine.validate_story"
        )
        template_name = outline.get("structure_template", DEFAULT_STRUCTURE_TEMPLATE)
        if template_name == DEFAULT_STRUCTURE_TEMPLATE:
            ADOSValidator.require_fields(
                outline["structure"], STRUCTURE_REQUIRED_FIELDS,
                location="StoryEngine.validate_story:structure",
            )
        else:
            structures = load_story_structures(project_path)
            template = structures["templates"].get(template_name)
            expected = template["sections"] if template else []
            missing = [
                section for section in expected
                if not outline["structure"].get(section)
            ]
            if template is None or missing:
                raise ADOSValidationError(
                    f"구조가 템플릿({template_name})과 맞지 않습니다. 누락: {missing}",
                    location="StoryEngine.validate_story:structure",
                    suggested_fix="config/story_structures.yaml의 sections를 확인하세요.",
                )
        return True
