# -*- coding: utf-8 -*-
"""Research engine (walking skeleton).

실제 웹 리서치 없이 더미 리서치 산출물을 만든다.
전체 스키마는 docs/17_RESEARCH_ENGINE.md 기준으로 이후 확장한다.

주의: 모든 출력은 dummy/placeholder이며 사실 정확성을 주장하지 않는다.
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

RESEARCH_DIR = "research"
BRIEF_FILE = "research_brief.json"

BRIEF_REQUIRED_FIELDS = [
    "project_id",
    "channel_id",
    "topic",
    "target_languages",
    "research_mode",
    "summary",
    "key_questions",
    "assumptions",
    "risks",
    "created_at",
]

DUMMY_DISCLAIMER = "Dummy research output. Placeholder only. Not fact-checked."


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ResearchEngine:
    def __init__(self, logger: ADOSLogger | None = None):
        self.logger = logger

    def brief_path(self, project_path: str | Path) -> Path:
        return Path(project_path) / RESEARCH_DIR / BRIEF_FILE

    def create_dummy_research(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        project = load_json(project_path / "project.json")
        topic = load_json(project_path / "topic.json")

        title = topic["title"]
        brief = {
            "project_id": project["project_id"],
            "channel_id": project["channel"]["channel_id"],
            "topic": title,
            "target_languages": project["languages"]["target_languages"],
            "research_mode": "dummy",
            "disclaimer": DUMMY_DISCLAIMER,
            "summary": f"'{title}' 주제에 대한 더미 리서치 요약. 실제 조사 결과가 아니다.",
            "key_questions": [
                f"{title} — 시청자가 가장 궁금해할 핵심 질문은 무엇인가?",
                "이 주제에서 가장 큰 오해는 무엇인가?",
                "전문가들이 동의하지 않는 지점은 어디인가?",
            ],
            "assumptions": [
                "실제 리서치가 아직 수행되지 않았다.",
                "모든 내용은 이후 실제 Research 단계에서 교체된다.",
            ],
            "risks": [
                "더미 데이터를 사실로 오인하면 안 된다.",
            ],
            "created_at": _now_iso(),
        }
        folder = project_path / RESEARCH_DIR
        write_json(folder / BRIEF_FILE, brief)
        write_json(
            folder / "research_questions.json",
            {
                "project_id": project["project_id"],
                "research_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "questions": brief["key_questions"],
                "created_at": _now_iso(),
            },
        )
        write_json(
            folder / "source_plan.json",
            {
                "project_id": project["project_id"],
                "research_mode": "dummy",
                "disclaimer": DUMMY_DISCLAIMER,
                "planned_source_types": [
                    "academic_papers",
                    "expert_interviews",
                    "trusted_news",
                ],
                "sources": [],
                "created_at": _now_iso(),
            },
        )
        if self.logger:
            self.logger.info(
                f"더미 리서치 생성: {project['project_id']}",
                metadata={"project_id": project["project_id"]},
            )
        return brief

    def load_research_brief(self, project_path: str | Path) -> dict:
        path = self.brief_path(project_path)
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"research_brief.json이 없습니다: {path}",
                location="ResearchEngine.load_research_brief",
                suggested_fix="create_dummy_research를 먼저 실행하세요.",
            )
        return load_json(path)

    def validate_research(self, project_path: str | Path) -> bool:
        brief = self.load_research_brief(project_path)
        ADOSValidator.require_fields(
            brief, BRIEF_REQUIRED_FIELDS, location="ResearchEngine.validate_research"
        )
        return True
