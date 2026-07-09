# -*- coding: utf-8 -*-
"""Full pipeline runner (walking skeleton).

기존 dummy 엔진들을 순서대로 실행해 전체 라이프사이클을 완주시킨다.
엔진 로직을 중복 구현하지 않고 상태 전환만 안전하게 관리한다.

Growth는 워크플로우 단계가 아니므로(STAGE_ORDER에 없음) ANALYTICS 완료 후
자문(advisory) 출력으로만 실행하고 stage 전환은 하지 않는다.
"""
from datetime import datetime, timezone
from pathlib import Path

from core import (
    ADOSLogger,
    ADOSPathManager,
    StageName,
    load_json,
    write_json,
)
from engines.ai_evolution import AIEvolutionEngine
from engines.analytics import AnalyticsEngine
from engines.channel import ChannelEngine
from engines.direction import DirectionEngine
from engines.editing import EditingEngine
from engines.growth import GrowthEngine
from engines.knowledge import KnowledgeEngine
from engines.learning import LearningEngine
from engines.motion import MotionEngine
from engines.project import ProjectEngine
from engines.publishing import PublishingEngine
from engines.quality import QualityEngine
from engines.research import ResearchEngine
from engines.story import StoryEngine
from engines.subtitle import SubtitleEngine
from engines.timeline import TimelineEngine
from engines.visual import VisualEngine
from engines.voice import VoiceEngine
from engines.workflow import WorkflowOrchestrator, WorkflowStateManager

SAMPLE_CHANNEL_REQUEST = {
    "channel_id": "future",
    "channel_name": "Future Lab",
    "template_id": "future_documentary_template",
    "language": "ko",
}

SAMPLE_PROJECT_REQUEST = {
    "channel_id": "future",
    "topic": "100만 년 후 인간은 어떤 모습일까?",
    "topic_slug": "million-year-human",
    "target_languages": ["ko", "en"],
    "duration_seconds": 900,
}

# 주요 산출물 경로 (요약용)
KEY_OUTPUTS = {
    "research_brief": "research/research_brief.json",
    "knowledge_map": "knowledge/knowledge_map.json",
    "story_outline": "story/story_outline.json",
    "direction_plan": "direction/direction_plan.json",
    "timeline": "timeline/timeline.json",
    "visual_plan": "assets/images/visual_plan.json",
    "motion_plan": "assets/motion/motion_plan.json",
    "voice_plan": "assets/audio/voice_plan.json",
    "subtitle_plan": "assets/subtitles/subtitle_plan.json",
    "editing_plan": "edit/editing_plan.json",
    "quality_report": "reports/quality_report.json",
    "package_manifest": "package/package_manifest.json",
    "ready_state": "package/ready_state.json",
    "published_record": "package/published_record.json",
    "analytics_snapshot": "analytics/performance_snapshot.json",
    "growth_report": "analytics/growth_report.json",
    "learning_report": "learning/learning_report.json",
    "ai_evolution_report": "ai_evolution/ai_evolution_report.json",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FullPipelineRunner:
    def __init__(self, path_manager: ADOSPathManager | None = None, logger: ADOSLogger | None = None):
        self.paths = path_manager or ADOSPathManager()
        self.logger = logger
        self.orchestrator = WorkflowOrchestrator(logger)

    # --- 준비 ---
    def _ensure_sample_channel(self) -> None:
        channel_id = SAMPLE_CHANNEL_REQUEST["channel_id"]
        if not (self.paths.channels / channel_id / "channel.yaml").is_file():
            ChannelEngine(self.paths).create_channel(dict(SAMPLE_CHANNEL_REQUEST))

    def create_sample_project(self) -> dict:
        self._ensure_sample_channel()
        return ProjectEngine(self.paths).create_project(dict(SAMPLE_PROJECT_REQUEST))

    # --- 실행 ---
    def run_full_dummy_pipeline(self, project_path: str | Path | None = None) -> dict:
        if project_path is None:
            project = self.create_sample_project()
            project_path = Path(project["path"])
        else:
            project_path = Path(project_path)

        if not WorkflowStateManager.state_path(project_path).is_file():
            self.orchestrator.initialize_workflow(project_path)

        self.run_until_ai_evolution(project_path)

        state = WorkflowStateManager.load_workflow_state(project_path)
        summary = {
            "project_id": state["project_id"],
            "project_path": str(project_path),
            "final_stage": state["current_stage"],
            "workflow_status": state["status"],
            "completed_stages": state["completed_stages"],
            "outputs": self.get_output_summary(project_path),
        }
        return summary

    def run_until_ai_evolution(self, project_path: str | Path) -> None:
        project_path = Path(project_path)
        publishing = PublishingEngine(self.logger)

        # INITIALIZED에서 시작하면 RESEARCH로 전진
        if WorkflowStateManager.get_current_stage(project_path) == str(StageName.INITIALIZED):
            self.orchestrator.advance_to_next_stage(project_path)

        handlers = [
            (StageName.RESEARCH, ResearchEngine(self.logger).create_dummy_research, KEY_OUTPUTS["research_brief"]),
            (StageName.KNOWLEDGE, KnowledgeEngine(self.logger).create_dummy_knowledge, KEY_OUTPUTS["knowledge_map"]),
            (StageName.STORY, StoryEngine(self.logger).create_dummy_story, KEY_OUTPUTS["story_outline"]),
            (StageName.DIRECTION, DirectionEngine(self.logger).create_dummy_direction, KEY_OUTPUTS["direction_plan"]),
            (StageName.TIMELINE, TimelineEngine(self.logger).create_dummy_timeline, KEY_OUTPUTS["timeline"]),
            (StageName.VISUAL, VisualEngine(self.logger).create_dummy_visual_plan, KEY_OUTPUTS["visual_plan"]),
            (StageName.MOTION, MotionEngine(self.logger).create_dummy_motion_plan, KEY_OUTPUTS["motion_plan"]),
            (StageName.VOICE, VoiceEngine(self.logger).create_dummy_voice_plan, KEY_OUTPUTS["voice_plan"]),
            (StageName.SUBTITLE, SubtitleEngine(self.logger).create_dummy_subtitle_plan, KEY_OUTPUTS["subtitle_plan"]),
            (StageName.EDITING, EditingEngine(self.logger).create_dummy_editing_plan, KEY_OUTPUTS["editing_plan"]),
            (StageName.QUALITY, QualityEngine(self.logger).create_dummy_quality_report, KEY_OUTPUTS["quality_report"]),
            (StageName.AUTO_FIX, None, None),  # gate PASS → skip
            (StageName.PACKAGE, publishing.create_dummy_package, KEY_OUTPUTS["package_manifest"]),
            (StageName.READY, publishing.create_dummy_ready_state, KEY_OUTPUTS["ready_state"]),
            (StageName.PUBLISHED, publishing.create_dummy_published_record, KEY_OUTPUTS["published_record"]),
            (StageName.ANALYTICS, AnalyticsEngine(self.logger).create_dummy_analytics, KEY_OUTPUTS["analytics_snapshot"]),
            (StageName.LEARNING, LearningEngine(self.logger).create_dummy_learning_report, KEY_OUTPUTS["learning_report"]),
            (StageName.AI_EVOLUTION, AIEvolutionEngine(self.logger).create_dummy_ai_evolution_report, KEY_OUTPUTS["ai_evolution_report"]),
        ]

        for stage, run, ref in handlers:
            if run is not None:
                run(project_path)
                result = {"plan_ref": ref, "mode": "dummy"}
            else:
                result = {"status": "SKIPPED", "reason": "quality gate PASS, auto_fix_required=false"}
            self.orchestrator.write_stage_result(project_path, str(stage), result)
            self.orchestrator.mark_stage_completed(project_path, str(stage), result_ref=ref)
            self.orchestrator.advance_to_next_stage(project_path)

            # Growth advisory — ANALYTICS 완료 직후, stage 전환 없이 실행
            if stage == StageName.ANALYTICS:
                GrowthEngine(self.logger).create_dummy_growth_report(project_path)
                write_json(
                    project_path / "workflow" / "stage_results" / "GROWTH_result.json",
                    {
                        "stage": "GROWTH",
                        "advisory": True,
                        "note": "Growth는 워크플로우 단계가 아니라 자문 출력이다.",
                        "created_at": _now_iso(),
                        "result": {"plan_ref": KEY_OUTPUTS["growth_report"], "mode": "dummy"},
                    },
                )

        # AI_EVOLUTION 완료 후 현재 단계는 COMPLETE — 완주를 깔끔하게 기록
        state = WorkflowStateManager.load_workflow_state(project_path)
        if state["current_stage"] == str(StageName.COMPLETE):
            state["status"] = "COMPLETED"
            WorkflowStateManager.save_workflow_state(project_path, state)

    # --- 요약 ---
    def get_output_summary(self, project_path: str | Path) -> dict:
        project_path = Path(project_path)
        return {
            key: {"path": rel, "exists": (project_path / rel).is_file()}
            for key, rel in KEY_OUTPUTS.items()
        }

    # --- 업로드 준비까지 포함한 전체 실행 ---
    def run_full_dummy_pipeline_with_upload_preparation(self) -> dict:
        """전체 dummy 파이프라인 완주 후 업로드 준비 산출물까지 생성한다.

        실자산 미등록·사람 검토 미승인 상태이므로 최종 upload_ready는
        false가 정상이다. PASS를 강제하지 않는다.
        """
        from engines.assets import AssetRegistry
        from engines.final_quality import FinalQualityGate
        from engines.reporting import OperationReportGenerator, RunReportGenerator
        from engines.review import HumanReviewEngine
        from engines.upload import UploadPreparer

        summary = self.run_full_dummy_pipeline()
        project_path = Path(summary["project_path"])

        RunReportGenerator(self.logger).create_run_report(project_path)

        registry = AssetRegistry(self.logger)
        registry.create_asset_requirements(project_path)
        registry.create_production_asset_manifest(project_path)
        registry.create_asset_readiness_report(project_path)

        HumanReviewEngine(self.logger).create_review_checkpoints(project_path)

        final_gate = FinalQualityGate(self.logger)
        final_report = final_gate.create_final_quality_report(project_path)

        preparer = UploadPreparer(self.logger)
        preparer.create_youtube_metadata_package(project_path)
        preparer.create_upload_readiness_checklist(project_path)
        preparer.create_manual_upload_instructions(project_path)

        operation = OperationReportGenerator(self.logger)
        operation_report = operation.create_operation_report(project_path)

        summary["upload_preparation"] = {
            "final_decision": final_report["final_decision"],
            "upload_ready": final_report["upload_ready"],
            "upload_blockers": final_report["upload_blockers"],
            "asset_readiness_report": str(registry.readiness_path(project_path)),
            "human_review_summary": str(project_path / "reports" / "human_review_summary.json"),
            "final_quality_report": str(final_gate.report_path(project_path)),
            "youtube_metadata_package": str(preparer.metadata_path(project_path)),
            "upload_readiness_checklist": str(preparer.checklist_path(project_path)),
            "operation_report": str(operation.report_path(project_path)),
            "next_manual_actions": operation_report["next_manual_actions"],
        }
        return summary
