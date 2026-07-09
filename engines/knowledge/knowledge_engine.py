# -*- coding: utf-8 -*-
"""Knowledge engine (walking skeleton).

더미 리서치 결과를 더미 지식 산출물로 정리한다.
전체 스키마는 docs/18_KNOWLEDGE_ENGINE.md 기준으로 이후 확장한다.

주의: 리서치가 dummy이므로 모든 fact는 placeholder이며 production-ready가 아니다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSValidator,
    load_json,
    write_json,
)

KNOWLEDGE_DIR = "knowledge"
MAP_FILE = "knowledge_map.json"

MAP_REQUIRED_FIELDS = [
    "project_id",
    "topic",
    "knowledge_mode",
    "core_concept",
    "supporting_points",
    "narrative_angles",
    "uncertainty_notes",
    "created_at",
]

DUMMY_DISCLAIMER = (
    "Dummy knowledge output. All facts are placeholders and NOT production-ready."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class KnowledgeEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def map_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / KNOWLEDGE_DIR / MAP_FILE

    def create_dummy_knowledge(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        brief_path = project_path / "research" / "research_brief.json"
        if not brief_path.is_file():
            raise ADOSFileNotFoundError(
                f"research_brief.json이 없습니다: {brief_path}",
                location="KnowledgeEngine.create_dummy_knowledge",
                suggested_fix="ResearchEngine.create_dummy_research를 먼저 실행하세요.",
            )
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")
        brief = load_json(brief_path)

        title = topic["title"]
        knowledge_map = {
            "project_id": project["project_id"],
            "topic": title,
            "knowledge_mode": "dummy",
            "disclaimer": DUMMY_DISCLAIMER,
            "core_concept": f"'{title}'의 핵심 개념 (placeholder).",
            "supporting_points": [
                "지지 포인트 1 (placeholder)",
                "지지 포인트 2 (placeholder)",
                "지지 포인트 3 (placeholder)",
            ],
            "narrative_angles": [
                "호기심 자극형 전개 (placeholder)",
                "시간 순 전개 (placeholder)",
            ],
            "uncertainty_notes": [
                "리서치가 dummy이므로 모든 내용의 사실성이 검증되지 않았다.",
            ],
            "created_at": _now_iso(),
        }
        folder = project_path / KNOWLEDGE_DIR
        write_json(folder / MAP_FILE, knowledge_map)
        write_json(
            folder / "fact_sheet.json",
            {
                "project_id": project["project_id"],
                "knowledge_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "production_ready": False,
                "facts": [
                    {
                        "claim": "placeholder fact 1",
                        "verified": False,
                        "source": None,
                    }
                ],
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "knowledge_gaps.json",
            {
                "project_id": project["project_id"],
                "knowledge_mode": "dummy",
                "gaps": list(brief.get("key_questions", [])),
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 지식 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return knowledge_map

    def load_knowledge_map(self, project_path: str | Path) -> dict:
        path = self.map_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"knowledge_map.json이 없습니다: {path}",
                location="KnowledgeEngine.load_knowledge_map",
                suggested_fix="create_dummy_knowledge를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_knowledge(self, project_path: str | Path) -> bool:
        knowledge_map = self.load_knowledge_map(project_path)
        ADOSValidator.require_fields(
            knowledge_map, MAP_REQUIRED_FIELDS,
            location="KnowledgeEngine.validate_knowledge",
        )
        return True
