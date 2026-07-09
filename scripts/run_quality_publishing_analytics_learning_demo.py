# -*- coding: utf-8 -*-
"""ADOS Quality → Publishing → Analytics → Learning walking skeleton 데모.

단계별(stage-specific) 디버깅용 데모다.
전체 파이프라인은 scripts/run_full_dummy_pipeline.py를 사용한다.

앞 단계(R→…→EDITING)는 기존 데모 로직을 재사용해 QUALITY까지 진행한 뒤,
QUALITY → AUTO_FIX(skip) → PACKAGE → READY → PUBLISHED → ANALYTICS → LEARNING을
더미로 수행하고 AI_EVOLUTION 단계로 전환한다.

실행: 프로젝트 루트에서  python scripts/run_quality_publishing_analytics_learning_demo.py
(실제 업로드·영상 생성·데이터 수집은 일어나지 않는다.)
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from core import ADOSPathManager, StageName  # noqa: E402
from engines.analytics import AnalyticsEngine  # noqa: E402
from engines.learning import LearningEngine  # noqa: E402
from engines.publishing import PublishingEngine  # noqa: E402
from engines.quality import QualityEngine  # noqa: E402
from engines.workflow import WorkflowOrchestrator  # noqa: E402
from run_motion_voice_subtitle_editing_demo import (  # noqa: E402
    run_motion_voice_subtitle_editing_demo,
)


def run_quality_publishing_analytics_learning_demo(
    path_manager: ADOSPathManager | None = None,
) -> dict:
    pm = path_manager or ADOSPathManager()

    # R→…→EDITING 완료 후 current_stage = QUALITY 상태로 시작
    upstream = run_motion_voice_subtitle_editing_demo(pm)
    project_path = Path(upstream["project_path"])
    orchestrator = WorkflowOrchestrator()

    quality = QualityEngine()
    publishing = PublishingEngine()
    analytics = AnalyticsEngine()
    learning = LearningEngine()

    def complete(stage: StageName, result: dict, ref: str | None = None) -> str:
        orchestrator.write_stage_result(project_path, str(stage), result)
        orchestrator.mark_stage_completed(project_path, str(stage), result_ref=ref)
        return orchestrator.advance_to_next_stage(project_path)

    # QUALITY
    quality.create_dummy_quality_report(project_path)
    complete(
        StageName.QUALITY,
        {"quality_report_ref": "reports/quality_report.json", "mode": "dummy"},
        ref="reports/quality_report.json",
    )

    # AUTO_FIX — 게이트가 PASS이고 auto_fix_required=false이므로 skip 처리
    complete(
        StageName.AUTO_FIX,
        {"status": "SKIPPED", "reason": "quality gate PASS, auto_fix_required=false"},
    )

    # PACKAGE
    publishing.create_dummy_package(project_path)
    complete(
        StageName.PACKAGE,
        {"package_manifest_ref": "package/package_manifest.json", "mode": "dummy"},
        ref="package/package_manifest.json",
    )

    # READY
    publishing.create_dummy_ready_state(project_path)
    complete(
        StageName.READY,
        {"ready_state_ref": "package/ready_state.json", "upload_ready": False},
        ref="package/ready_state.json",
    )

    # PUBLISHED — 시뮬레이션 기록만 (실제 업로드 없음)
    publishing.create_dummy_published_record(project_path)
    complete(
        StageName.PUBLISHED,
        {
            "published_record_ref": "package/published_record.json",
            "publication_status": "SIMULATED_NOT_UPLOADED",
        },
        ref="package/published_record.json",
    )

    # ANALYTICS
    analytics.create_dummy_analytics(project_path)
    complete(
        StageName.ANALYTICS,
        {"snapshot_ref": "analytics/performance_snapshot.json", "data_ready": False},
        ref="analytics/performance_snapshot.json",
    )

    # LEARNING
    learning.create_dummy_learning_report(project_path)
    current_stage = complete(
        StageName.LEARNING,
        {"learning_report_ref": "learning/learning_report.json", "mode": "dummy"},
        ref="learning/learning_report.json",
    )

    return {
        "project_id": upstream["project_id"],
        "project_path": str(project_path),
        "quality_report_path": str(quality.report_path(project_path)),
        "package_manifest_path": str(publishing.manifest_path(project_path)),
        "published_record_path": str(publishing.published_record_path(project_path)),
        "analytics_snapshot_path": str(analytics.snapshot_path(project_path)),
        "learning_report_path": str(learning.report_path(project_path)),
        "current_stage": current_stage,
    }


def main() -> int:
    result = run_quality_publishing_analytics_learning_demo()
    print(f"project_id             : {result['project_id']}")
    print(f"project path           : {result['project_path']}")
    print(f"quality_report path    : {result['quality_report_path']}")
    print(f"package_manifest path  : {result['package_manifest_path']}")
    print(f"published_record path  : {result['published_record_path']}")
    print(f"analytics_snapshot path: {result['analytics_snapshot_path']}")
    print(f"learning_report path   : {result['learning_report_path']}")
    print(f"current_stage          : {result['current_stage']} (LEARNING 완료 후)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
