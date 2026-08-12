# -*- coding: utf-8 -*-
"""Production 테스트 공용 헬퍼 — 임시 ADOS 루트와 미니 production 템플릿."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ADOSPathManager, write_yaml  # noqa: E402

MINI_TEMPLATE_ID = "mini_production_template"


def make_temp_root(tmp: Path) -> ADOSPathManager:
    for d in ("docs", "config", "templates", "channels", "projects", "logs"):
        (tmp / d).mkdir(parents=True, exist_ok=True)
    return ADOSPathManager(tmp)


def mini_pipeline_stages() -> list[dict]:
    return [
        {
            "id": "T_INTAKE", "title": "접수", "description": "",
            "kind": "deterministic", "owner_role": "platform_operations",
            "executor": "project.intake",
            "requires": [], "produces": ["project_intake"], "depends_on": [],
            "approval": None, "retry_policy": {"max_attempts": 3},
            "external_side_effect": False, "cost_tracking": False, "enabled": True,
        },
        {
            "id": "T_RESEARCH", "title": "조사", "description": "",
            "kind": "creative_workflow", "owner_role": "strategy_market_intelligence",
            "executor": "longform.opportunity_research",
            "requires": ["project_intake"], "produces": ["opportunity_research"],
            "depends_on": ["T_INTAKE"],
            "approval": None, "retry_policy": {"max_attempts": 3},
            "external_side_effect": False, "cost_tracking": True, "enabled": True,
        },
        {
            "id": "T_GATE", "title": "승인", "description": "",
            "kind": "human_gate", "owner_role": "executive_editor",
            "executor": "approval.concept",
            "requires": ["opportunity_research"], "produces": ["concept_approval"],
            "depends_on": ["T_RESEARCH"],
            "approval": {"approvers": ["executive_editor"],
                         "decisions": ["APPROVE", "REQUEST_REVISION", "REJECT"]},
            "retry_policy": {"max_attempts": 3},
            "external_side_effect": False, "cost_tracking": False, "enabled": True,
        },
        {
            "id": "T_ASSETS", "title": "자산", "description": "",
            "kind": "provider_job", "owner_role": "production_operations",
            "executor": "provider.asset_production",
            "requires": ["concept_approval"], "produces": ["production_assets"],
            "depends_on": ["T_GATE"],
            "approval": None, "retry_policy": {"max_attempts": 3},
            "external_side_effect": False, "cost_tracking": True, "enabled": True,
        },
    ]


def mini_roles() -> dict:
    return {"roles": [
        {"role_id": rid, "name": rid, "responsibility": "test",
         "allowed_step_kinds": kinds, "required_inputs": [], "expected_outputs": [],
         "can_approve": rid == "executive_editor",
         "can_trigger_external_action": rid == "production_operations",
         "kpi": [], "failure_conditions": []}
        for rid, kinds in [
            ("platform_operations", ["deterministic"]),
            ("strategy_market_intelligence", ["creative_workflow"]),
            ("executive_editor", ["human_gate"]),
            ("production_operations", ["provider_job"]),
        ]
    ]}


def mini_quality() -> dict:
    return {
        "quality_rules": {
            "technical": [{"rule_id": "tech.required_files",
                           "description": "필수 파일", "severity": "BLOCKER"}],
            "editorial": [],
            "trust_and_safety": [],
        },
        "gate": {"results": ["PASS", "HUMAN_REVIEW_REQUIRED", "REVISION_REQUIRED", "BLOCKED"],
                 "default_state": "UNASSESSED", "subtitle_max_cps": 12,
                 "min_resolution": {"width": 1920, "height": 1080}},
    }


def mini_form() -> dict:
    return {"form_id": "mini_form", "form_version": "1.0.0", "fields": [
        {"name": "topic", "type": "string", "required": True},
        {"name": "target_duration_seconds", "type": "integer", "required": True, "default": 900},
        {"name": "language", "type": "string", "required": True, "default": "ko"},
        {"name": "factuality_mode", "type": "string", "required": True,
         "default": "fact_plus_scenario",
         "enum": ["strict_fact", "fact_plus_scenario", "fiction_labeled"]},
        {"name": "approval_mode", "type": "string", "required": True,
         "default": "human_review", "enum": ["human_review", "assisted_auto"]},
    ]}


def mini_view() -> dict:
    return {"view_id": "mini_view", "view_version": "1.0.0", "kpis": [
        {"key": "target_duration_seconds", "label": "목표 길이",
         "source": "project_inputs.target_duration_seconds"},
    ], "tabs": [
        {"id": "overview", "title": "개요", "stages": ["T_INTAKE"],
         "artifacts": ["project_intake"], "cards": ["pipeline_progress"]},
        {"id": "work", "title": "작업", "stages": ["T_RESEARCH", "T_GATE", "T_ASSETS"],
         "artifacts": ["opportunity_research", "concept_approval", "production_assets"],
         "cards": ["stage_status"]},
    ]}


def write_mini_template(
    pm: ADOSPathManager,
    template_id: str = MINI_TEMPLATE_ID,
    stages: list[dict] | None = None,
    view: dict | None = None,
    roles: dict | None = None,
) -> Path:
    folder = pm.templates / template_id
    write_yaml(folder / "template.yaml", {
        "template_id": template_id, "name": "Mini Production", "version": "1.0.0",
        "template_version": "1.0.0", "status": "ACTIVE", "category": "test",
        "description": "test bundle", "default_language": "ko",
        "supported_languages": ["ko"],
        "content_type": "test_content",
        "pipeline_file": "pipeline.yaml", "project_form_file": "project_form.yaml",
        "project_view_file": "project_view.yaml", "roles_file": "roles.yaml",
        "quality_file": "quality.yaml",
        "recommended_duration_seconds": {"min": 600, "max": 1200},
        "allowed_duration_seconds": {"max": 1800},
    })
    write_yaml(folder / "pipeline.yaml", {
        "pipeline_id": "mini_pipeline_v1", "pipeline_version": "1.0.0",
        "description": "test", "stages": stages or mini_pipeline_stages(),
    })
    write_yaml(folder / "roles.yaml", roles or mini_roles())
    write_yaml(folder / "quality.yaml", mini_quality())
    write_yaml(folder / "project_form.yaml", mini_form())
    write_yaml(folder / "project_view.yaml", view or mini_view())
    return folder


def make_production_project(pm: ADOSPathManager, template_id: str = MINI_TEMPLATE_ID,
                            channel_id: str = "test_channel", topic: str = "테스트 주제",
                            duration: int = 900) -> Path:
    from engines.channel import ChannelEngine
    from engines.project import ProjectEngine

    if not (pm.channels / channel_id / "channel.yaml").is_file():
        ChannelEngine(pm).create_channel({
            "channel_id": channel_id, "channel_name": "Test Channel",
            "template_id": template_id, "language": "ko",
        })
    result = ProjectEngine(pm).create_project({
        "channel_id": channel_id, "topic": topic,
        "target_languages": ["ko"], "duration_seconds": duration,
        "production_mode": True,
    })
    return Path(result["path"])


def good_research_result() -> dict:
    return {
        "competitor_landscape": ["채널A 10만 구독"],
        "audience_demand_signals": ["검색량 상승"],
        "opportunity_hypotheses": ["빈 포지션 존재"],
        "risks": ["포화"],
        "recommendation": "진행",
    }
