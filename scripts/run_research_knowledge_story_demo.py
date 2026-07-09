# -*- coding: utf-8 -*-
"""ADOS Research → Knowledge → Story walking skeleton 데모.

단계별(stage-specific) 디버깅용 데모다.
전체 파이프라인은 scripts/run_full_dummy_pipeline.py를 사용한다.

흐름: 채널 준비 → 프로젝트 생성 → workflow 초기화 → RESEARCH → KNOWLEDGE
      → STORY 순서로 더미 산출물 생성·완료 → DIRECTION 단계로 전환

실행: 프로젝트 루트에서  python scripts/run_research_knowledge_story_demo.py
(Timeline은 여기서 실행하지 않는다 — Direction 이후 단계.)
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from core import ADOSPathManager, StageName  # noqa: E402
from engines.knowledge import KnowledgeEngine  # noqa: E402
from engines.research import ResearchEngine  # noqa: E402
from engines.story import StoryEngine  # noqa: E402
from engines.workflow import WorkflowOrchestrator, WorkflowStateManager  # noqa: E402
from create_sample_channel import channel_exists, create_sample_channel  # noqa: E402
from create_sample_project import create_sample_project  # noqa: E402


def run_research_knowledge_story_demo(
    path_manager: ADOSPathManager | None = None,
) -> dict:
    pm = path_manager or ADOSPathManager()

    if not channel_exists(pm):
        create_sample_channel(pm)

    project = create_sample_project(pm)
    project_path = Path(project["path"])

    orchestrator = WorkflowOrchestrator()
    orchestrator.initialize_workflow(project_path)

    # INITIALIZED에서 시작하면 RESEARCH로 전진, 이미 RESEARCH면 그대로 둔다.
    if WorkflowStateManager.get_current_stage(project_path) == str(StageName.INITIALIZED):
        orchestrator.advance_to_next_stage(project_path)

    research = ResearchEngine()
    research.create_dummy_research(project_path)
    orchestrator.write_stage_result(
        project_path, str(StageName.RESEARCH),
        {"research_brief_ref": "research/research_brief.json", "mode": "dummy"},
    )
    orchestrator.mark_stage_completed(
        project_path, str(StageName.RESEARCH), result_ref="research/research_brief.json"
    )
    orchestrator.advance_to_next_stage(project_path)  # → KNOWLEDGE

    knowledge = KnowledgeEngine()
    knowledge.create_dummy_knowledge(project_path)
    orchestrator.write_stage_result(
        project_path, str(StageName.KNOWLEDGE),
        {"knowledge_map_ref": "knowledge/knowledge_map.json", "mode": "dummy"},
    )
    orchestrator.mark_stage_completed(
        project_path, str(StageName.KNOWLEDGE), result_ref="knowledge/knowledge_map.json"
    )
    orchestrator.advance_to_next_stage(project_path)  # → STORY

    story = StoryEngine()
    story.create_dummy_story(project_path)
    orchestrator.write_stage_result(
        project_path, str(StageName.STORY),
        {"story_outline_ref": "story/story_outline.json", "mode": "dummy"},
    )
    orchestrator.mark_stage_completed(
        project_path, str(StageName.STORY), result_ref="story/story_outline.json"
    )
    current_stage = orchestrator.advance_to_next_stage(project_path)  # → DIRECTION

    return {
        "project_id": project["project_id"],
        "project_path": str(project_path),
        "research_brief_path": str(research.brief_path(project_path)),
        "knowledge_map_path": str(knowledge.map_path(project_path)),
        "story_outline_path": str(story.outline_path(project_path)),
        "current_stage": current_stage,
    }


def main() -> int:
    result = run_research_knowledge_story_demo()
    print(f"project_id          : {result['project_id']}")
    print(f"project path        : {result['project_path']}")
    print(f"research_brief path : {result['research_brief_path']}")
    print(f"knowledge_map path  : {result['knowledge_map_path']}")
    print(f"story_outline path  : {result['story_outline_path']}")
    print(f"current_stage       : {result['current_stage']} (STORY 완료 후)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
