# -*- coding: utf-8 -*-
"""Production executors — allowlist에 등록되는 실제 handler 구현.

원칙:
- creative_workflow에 실제 LLM adapter가 연결되지 않은 현재, 더미 내용을 만들어
  COMPLETED 처리하지 않는다. 대신 work order를 만들고 WAITING_INPUT으로 둔다.
  사람이 Claude/ChatGPT 결과를 작성해 import하면 출력 스키마 검증 후에만 완료한다.
- placeholder/dummy/sample disclaimer가 있는 결과는 production 산출물로 통과 금지.
- deterministic 단계(합성·검사·패키지)는 일반 코드가 수행한다.
- 외부 호출은 하지 않는다. provider_job은 작업 기록만 만든다.
"""
import shutil
from datetime import datetime, timezone
from pathlib import Path

from core import load_json, load_yaml, write_json

from .executor_registry import (
    ExecutionContext,
    ExecutorRegistry,
    ExecutorResult,
    scan_for_placeholders,
)

WORK_ORDERS_DIR = Path("workflow") / "work_orders"
APPROVALS_DIR = Path("workflow") / "approvals"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# creative workflow 스키마 정의
#   string  → 비어 있지 않은 문자열
#   list    → 리스트 (빈 리스트 허용)
#   list+   → 비어 있지 않은 리스트
#   number  → int/float
#   any     → 존재만 확인
# ---------------------------------------------------------------------------
CREATIVE_SPECS = {
    "longform.opportunity_research": {
        "artifact": "opportunity_research",
        "output_rel": "research/opportunity_research.json",
        "schema": {
            "competitor_landscape": "list+",
            "audience_demand_signals": "list+",
            "opportunity_hypotheses": "list+",
            "risks": "list",
            "recommendation": "string",
        },
        "instructions": "경쟁 채널/수요 신호를 조사해 이 주제의 기회 가설과 추천 방향을 작성한다.",
    },
    "longform.strategy": {
        "artifact": "content_strategy",
        "output_rel": "research/content_strategy.json",
        "schema": {
            "target_viewer": "string",
            "viewer_problem_or_desire": "string",
            "core_promise": "string",
            "unique_angle": "string",
            "why_now": "string",
            "differentiation_from_competitors": "string",
            "previous_channel_video_difference": "string",
            "emotional_arc": "any",
            "educational_or_entertainment_value": "string",
            "success_hypothesis": "string",
            "title_hypotheses": "list+",
            "thumbnail_hypotheses": "list+",
            "production_difficulty": "string",
            "estimated_cost_range": "any",
            "policy_risks": "list",
            "rejected_alternatives": "list",
            "final_recommendation": "string",
        },
        "instructions": "이 프로젝트의 콘텐츠 전략을 확정한다. 근거 없는 낙관 금지, 기각한 대안도 기록한다.",
    },
    "longform.evidence_research": {
        "artifact": "evidence_research",
        "output_rel": "research/evidence_research.json",
        "schema": {
            "sources": "list+",
            "claims": "list+",
            "source_for_each_claim": "any",
            "fact_or_scenario": "any",
            "confidence": "any",
            "uncertainty": "any",
            "prohibited_or_high_risk_claims": "list",
            "citation_notes": "any",
        },
        "instructions": "대본에 쓸 주장별 출처를 정리한다. 사실과 가상 시나리오를 명확히 분리한다.",
    },
    "longform.script": {
        "artifact": "story_script",
        "output_rel": "story/story_script.json",
        "schema": {
            "hook": "string",
            "viewer_question": "string",
            "act_structure": "list+",
            "narration_blocks": "list+",
            "scene_intents": "list+",
            "open_loops": "list",
            "payoff": "string",
            "ending": "string",
            "estimated_duration_seconds": "number",
            "words_per_minute": "number",
            "source_claim_refs": "list",
            "originality_notes": "string",
        },
        "instructions": "훅→질문→막 구조→페이오프 순의 롱폼 대본. 모든 주장은 evidence_research의 claim을 참조한다.",
    },
    "longform.direction": {
        "artifact": "direction_asset_plan",
        "output_rel": "direction/direction_asset_plan.json",
        "schema": {
            "act_visual_language": "any",
            "scene_directions": "list+",
            "shots": "list+",
            "narration_voice": "any",
            "provider_requirements": "any",
        },
        "instructions": "장면 연출과 샷 단위 자산 계획(이미지/모션/음성)을 작성한다.",
    },
    "longform.asset_plan": {
        "artifact": "asset_plan",
        "output_rel": "direction/asset_plan.json",
        "schema": {
            "shots": "list+",
            "provider_requirements": "any",
        },
        "instructions": "샷 단위 자산 계획을 작성한다.",
    },
}

_SCHEMA_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str) and v.strip() != "",
    "list": lambda v: isinstance(v, list),
    "list+": lambda v: isinstance(v, list) and len(v) > 0,
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "any": lambda v: v is not None,
}


def validate_creative_result(result: dict, schema: dict) -> list[str]:
    """import된 결과를 스키마로 검증한다. 문제 목록 반환."""
    problems = []
    if not isinstance(result, dict):
        return ["결과는 JSON object여야 합니다"]
    for field_name, kind in schema.items():
        if field_name not in result:
            problems.append(f"필수 필드 누락: {field_name}")
            continue
        if not _SCHEMA_TYPE_CHECKS[kind](result[field_name]):
            problems.append(f"필드 형식 오류: {field_name} (기대: {kind})")
    return problems


# ---------------------------------------------------------------------------
# 공통 handler
# ---------------------------------------------------------------------------
def creative_workflow_executor(ctx: ExecutionContext) -> ExecutorResult:
    spec = CREATIVE_SPECS[ctx.stage["executor"]]
    stage_id = ctx.stage["id"]
    work_order_path = ctx.project_path / WORK_ORDERS_DIR / f"{stage_id}.json"

    if ctx.imported_result is None:
        # 실제 LLM adapter 미연결 — work order 생성 후 사람 입력 대기
        inputs = {}
        for key in ctx.stage.get("requires") or []:
            entry = ctx.artifacts.get(key)
            if entry:
                inputs[key] = entry["relative_path"]
        write_json(work_order_path, {
            "stage_id": stage_id,
            "executor": ctx.stage["executor"],
            "instructions": spec["instructions"],
            "required_inputs": inputs,
            "output_schema": spec["schema"],
            "output_artifact_key": spec["artifact"],
            "output_rel": spec["output_rel"],
            "how_to_complete": (
                "결과 JSON을 작성한 뒤 실행: "
                f"python scripts/ados.py project import-result <PROJECT_PATH> {stage_id} <RESULT_FILE>"
            ),
            "created_at": _now_iso(),
        })
        return ExecutorResult(
            status="WAITING_INPUT",
            warnings=[f"LLM adapter 미연결 — work order 생성됨: {WORK_ORDERS_DIR / (stage_id + '.json')}"],
            metrics={"work_order": str(WORK_ORDERS_DIR / f"{stage_id}.json").replace("\\", "/")},
        )

    # import된 결과 검증
    problems = validate_creative_result(ctx.imported_result, spec["schema"])
    if problems:
        return ExecutorResult(status="FAILED",
                              blockers=[f"결과 스키마 검증 실패: {p}" for p in problems])
    placeholders = scan_for_placeholders(ctx.imported_result)
    if placeholders:
        return ExecutorResult(
            status="FAILED",
            blockers=[f"placeholder 감지 — production 산출물로 통과 불가: {p}"
                      for p in placeholders[:5]],
        )
    output_path = ctx.project_path / spec["output_rel"]
    write_json(output_path, {
        "stage_id": stage_id,
        "imported_from": ctx.imported_result_ref,
        "imported_at": _now_iso(),
        "result": ctx.imported_result,
    })
    return ExecutorResult(status="COMPLETED", outputs={spec["artifact"]: spec["output_rel"]})


def _approval_display(ctx: ExecutionContext) -> dict:
    """게이트별로 사람이 봐야 할 내용을 구성한다."""
    executor = ctx.stage["executor"]
    display: dict = {}
    if executor == "approval.concept":
        strategy = _load_artifact_result(ctx, "content_strategy")
        if strategy:
            display = {k: strategy.get(k) for k in (
                "target_viewer", "core_promise", "unique_angle", "success_hypothesis",
                "title_hypotheses", "policy_risks", "estimated_cost_range",
                "production_difficulty", "final_recommendation",
            )}
    elif executor == "approval.script":
        script = _load_artifact_result(ctx, "story_script")
        if script:
            display = {k: script.get(k) for k in (
                "hook", "viewer_question", "act_structure", "payoff", "ending",
                "estimated_duration_seconds", "originality_notes",
            )}
    elif executor == "approval.assets":
        entry = ctx.artifacts.get("production_assets")
        if entry:
            manifest = load_json(ctx.project_path / entry["relative_path"])
            blocks = manifest.get("blocks") or []
            display = {
                "block_count": len(blocks),
                "cut_count": sum(len(b.get("cuts") or []) for b in blocks),
                "manifest": entry["relative_path"],
            }
    elif executor == "approval.publish":
        entry = ctx.artifacts.get("upload_package")
        if entry:
            package = load_json(ctx.project_path / entry["relative_path"])
            display = {k: package.get(k) for k in (
                "video", "thumbnail", "title", "description", "tags", "chapters",
                "visibility", "ai_content_disclosure_required", "copyright_check",
            )}
    return display


def _load_artifact_result(ctx: ExecutionContext, key: str) -> dict | None:
    entry = ctx.artifacts.get(key)
    if not entry:
        return None
    data = load_json(ctx.project_path / entry["relative_path"])
    return data.get("result", data)


def human_gate_executor(ctx: ExecutionContext) -> ExecutorResult:
    stage_id = ctx.stage["id"]
    approval = ctx.stage.get("approval") or {}
    request_path = ctx.project_path / APPROVALS_DIR / f"{stage_id}_request.json"
    write_json(request_path, {
        "stage_id": stage_id,
        "approvers": approval.get("approvers") or [ctx.stage.get("owner_role")],
        "decisions": approval.get("decisions") or ["APPROVE", "REQUEST_REVISION", "REJECT"],
        "display": _approval_display(ctx),
        "how_to_decide": (
            f"python scripts/ados.py project approve <PROJECT_PATH> {stage_id} "
            "--decision APPROVE --reviewer human"
        ),
        "created_at": _now_iso(),
    })
    return ExecutorResult(
        status="WAITING_APPROVAL",
        metrics={"approval_request": str(APPROVALS_DIR / f"{stage_id}_request.json").replace("\\", "/")},
    )


def intake_executor(ctx: ExecutionContext) -> ExecutorResult:
    project_inputs = ctx.project.get("project_inputs") or {}
    form = (ctx.bundle or {}).get("project_form") or {}
    problems: list[str] = []
    warnings: list[str] = []
    for field_def in form.get("fields") or []:
        name = field_def["name"]
        if field_def.get("required") and (name not in project_inputs or project_inputs[name] in (None, "")):
            problems.append(f"필수 입력 누락: {name}")
        enum = field_def.get("enum")
        if enum and project_inputs.get(name) is not None and project_inputs[name] not in enum:
            problems.append(f"허용되지 않는 값: {name}={project_inputs[name]}")
    meta = (ctx.bundle or {}).get("template") or {}
    duration = project_inputs.get("target_duration_seconds")
    recommended = meta.get("recommended_duration_seconds") or {}
    allowed = meta.get("allowed_duration_seconds") or {}
    if isinstance(duration, (int, float)):
        if allowed.get("max") and duration > allowed["max"]:
            problems.append(f"목표 길이 {duration}s가 hard maximum {allowed['max']}s 초과")
        elif recommended and not (recommended.get("min", 0) <= duration <= recommended.get("max", 10**9)):
            warnings.append(
                f"목표 길이 {duration}s가 권장 범위({recommended.get('min')}~{recommended.get('max')}s) 밖"
            )
    if problems:
        return ExecutorResult(status="BLOCKED", blockers=problems, warnings=warnings)
    output_rel = "reports/project_intake.json"
    write_json(ctx.project_path / output_rel, {
        "stage_id": ctx.stage["id"],
        "project_inputs": project_inputs,
        "warnings": warnings,
        "validated": True,
        "created_at": _now_iso(),
    })
    return ExecutorResult(status="COMPLETED",
                          outputs={"project_intake": output_rel}, warnings=warnings)


def provider_job_executor(ctx: ExecutionContext) -> ExecutorResult:
    from engines.provider_jobs import ProviderJobManager

    stage_id = ctx.stage["id"]
    if ctx.imported_result is None:
        # 작업(job) 기록 생성 + 사람이 배치할 자산 manifest 형식 안내 — 외부 호출 없음
        plan_entry = ctx.artifacts.get("direction_asset_plan")
        plan = _load_artifact_result(ctx, "direction_asset_plan") or {}
        shots = plan.get("shots") or []
        image_count = sum(1 for s in shots if s.get("type", "image") == "image")
        motion_count = sum(1 for s in shots if s.get("type") == "motion")
        manager = ProviderJobManager()
        if not manager.queue_path(ctx.project_path).is_file():
            manager.create_job_queue(ctx.project_path)
        jobs = []
        source_ref = plan_entry["relative_path"] if plan_entry else "direction/direction_asset_plan.json"
        if image_count:
            jobs.append(manager.create_provider_job(
                ctx.project_path, "midjourney", "image_generation",
                source_ref, {"shot_count": image_count}))
        if motion_count:
            jobs.append(manager.create_provider_job(
                ctx.project_path, "midjourney_video", "motion_generation",
                source_ref, {"shot_count": motion_count}))
        jobs.append(manager.create_provider_job(
            ctx.project_path, "typecast", "narration_generation",
            source_ref, {"note": "narration blocks per script"}))
        write_json(ctx.project_path / WORK_ORDERS_DIR / f"{stage_id}.json", {
            "stage_id": stage_id,
            "executor": ctx.stage["executor"],
            "instructions": (
                "provider job에 따라 자산을 제작해 프로젝트 안에 배치한 뒤, "
                "production manifest JSON을 import한다."
            ),
            "expected_result_format": {
                "assets_root": "assets/production (프로젝트 상대 경로)",
                "fps": 25,
                "blocks": [{
                    "id": "NB001", "text": "블록 나레이션 텍스트",
                    "audio": "audio/NB001.wav",
                    "cuts": [{"id": "S01", "image": "images/S01.png", "kb": "zi"},
                             {"id": "S02", "motion": "motion/S02.mp4"}],
                }],
            },
            "jobs": [j["job_id"] for j in jobs],
            "how_to_complete": (
                f"python scripts/ados.py project import-result <PROJECT_PATH> {stage_id} <MANIFEST_FILE>"
            ),
            "created_at": _now_iso(),
        })
        for job in jobs:
            ctx.costs.append(stage_id, job["provider_name"], job_id=job["job_id"],
                             status="UNKNOWN")
        return ExecutorResult(
            status="WAITING_EXTERNAL",
            metrics={"provider_jobs": [j["job_id"] for j in jobs]},
            cost=None,
            external_call_made=False,
        )

    # import: production manifest 검증 (모든 자산 실존 확인)
    from engines.composition.longform_composition import LongformCompositionExecutor

    manifest = ctx.imported_result
    placeholders = scan_for_placeholders(manifest)
    try:
        LongformCompositionExecutor().validate_manifest(ctx.project_path, manifest)
    except Exception as e:
        return ExecutorResult(status="FAILED", blockers=[f"manifest 검증 실패: {e}"])
    if placeholders:
        return ExecutorResult(
            status="FAILED",
            blockers=[f"placeholder 감지: {p}" for p in placeholders[:5]],
        )
    output_rel = "assets/production_assets.json"
    write_json(ctx.project_path / output_rel, {
        "stage_id": stage_id,
        "imported_from": ctx.imported_result_ref,
        "imported_at": _now_iso(),
        "manifest": manifest,
    })
    return ExecutorResult(status="COMPLETED", outputs={"production_assets": output_rel})


def composition_executor(ctx: ExecutionContext) -> ExecutorResult:
    from engines.composition.longform_composition import LongformCompositionExecutor

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        return ExecutorResult(
            status="FAILED",
            blockers=["ffmpeg/ffprobe가 PATH에 없습니다 — 합성 불가. 설치 후 retry 하세요."],
        )
    entry = ctx.artifacts.get("production_assets")
    if not entry:
        return ExecutorResult(status="BLOCKED", blockers=["production_assets artifact 없음"])
    manifest = load_json(ctx.project_path / entry["relative_path"]).get("manifest", {})

    channel_id = (ctx.project.get("channel") or {}).get("channel_id")
    brand_path = ctx.root / "channels" / str(channel_id) / "brand_profile.yaml"
    brand_profile = load_yaml(brand_path) if brand_path.is_file() else {}
    styles_path = ctx.root / "config" / "subtitle_styles.yaml"
    if not styles_path.is_file():
        return ExecutorResult(status="FAILED",
                              blockers=[f"config/subtitle_styles.yaml이 없습니다: {styles_path}"])
    subtitle_styles = load_yaml(styles_path)

    output_rel = "assets/video/final_video_subtitled.mp4"
    executor = LongformCompositionExecutor()
    try:
        report = executor.compose(
            ctx.project_path, manifest, brand_profile, subtitle_styles,
            output_rel=output_rel, force=ctx.force,
            quality_rules=(ctx.bundle or {}).get("quality") or {},
        )
    except Exception as e:
        return ExecutorResult(status="FAILED", blockers=[f"합성 실패: {e}"])

    report_rel = "reports/composition_report.json"
    write_json(ctx.project_path / report_rel, report)
    if report["status"] != "PASS":
        return ExecutorResult(
            status="FAILED",
            blockers=[f"합성 검증 실패: duration_match={report['duration_match']}, "
                      f"subtitles_visible={report.get('subtitles_visible')}"],
            outputs={"composition_report": report_rel},
        )
    return ExecutorResult(
        status="COMPLETED",
        outputs={"final_video": output_rel, "composition_report": report_rel},
        metrics={"duration_seconds": report["output_duration_seconds"],
                 "display_cues": report["display_cue_count"]},
    )


def quality_safety_executor(ctx: ExecutionContext) -> ExecutorResult:
    from engines.quality.production_quality_gate import ProductionQualityGate

    video_entry = ctx.artifacts.get("final_video")
    comp_entry = ctx.artifacts.get("composition_report")
    composition_report = (
        load_json(ctx.project_path / comp_entry["relative_path"]) if comp_entry else None
    )
    meta = (ctx.bundle or {}).get("template") or {}
    gate = ProductionQualityGate()
    report = gate.assess(
        ctx.project_path,
        quality_rules=(ctx.bundle or {}).get("quality") or {},
        video_rel=video_entry["relative_path"] if video_entry else None,
        composition_report=composition_report,
        strategy=_load_artifact_result(ctx, "content_strategy"),
        script=_load_artifact_result(ctx, "story_script"),
        research=_load_artifact_result(ctx, "evidence_research"),
        project_inputs=ctx.project.get("project_inputs"),
        allowed_duration=meta.get("allowed_duration_seconds"),
    )
    report_rel = "reports/quality_safety_report.json"
    write_json(ctx.project_path / report_rel, report)
    outputs = {"quality_safety_report": report_rel}

    if report["result"] == "PASS":
        return ExecutorResult(status="COMPLETED", outputs=outputs)
    if report["result"] == "HUMAN_REVIEW_REQUIRED":
        stage_id = ctx.stage["id"]
        write_json(ctx.project_path / APPROVALS_DIR / f"{stage_id}_request.json", {
            "stage_id": stage_id,
            "reason": "quality gate HUMAN_REVIEW_REQUIRED",
            "unassessed": report["unassessed"],
            "report": report_rel,
            "how_to_decide": (
                f"python scripts/ados.py project approve <PROJECT_PATH> {stage_id} "
                "--decision APPROVE --reviewer human"
            ),
            "created_at": _now_iso(),
        })
        return ExecutorResult(
            status="WAITING_APPROVAL", outputs=outputs,
            warnings=[f"사람 검토 필요 항목 {len(report['unassessed'])}건"],
        )
    # REVISION_REQUIRED / BLOCKED
    return ExecutorResult(
        status="BLOCKED", outputs=outputs,
        blockers=report["blockers"] + report["failures"],
    )


def package_executor(ctx: ExecutionContext) -> ExecutorResult:
    video_entry = ctx.artifacts.get("final_video")
    quality_entry = ctx.artifacts.get("quality_safety_report")
    if not video_entry or not quality_entry:
        return ExecutorResult(status="BLOCKED",
                              blockers=["final_video 또는 quality_safety_report 없음"])
    quality_report = load_json(ctx.project_path / quality_entry["relative_path"])
    if quality_report.get("blockers"):
        return ExecutorResult(
            status="BLOCKED",
            blockers=["quality blocker 미해결 상태로 PACKAGE_READY 진행 불가"]
            + quality_report["blockers"],
        )
    strategy = _load_artifact_result(ctx, "content_strategy") or {}
    script = _load_artifact_result(ctx, "story_script") or {}

    titles = strategy.get("title_hypotheses") or []
    title = titles[0] if titles else (ctx.project.get("topic") or {}).get("title", "")
    description_parts = [p for p in (script.get("hook"), strategy.get("core_promise")) if p]
    thumbnail_entry = ctx.artifacts.get("thumbnail")
    warnings = []
    if not thumbnail_entry:
        warnings.append("썸네일 artifact 없음 — 게시 승인 전 준비 필요")

    chapters = []
    for i, act in enumerate(script.get("act_structure") or [], 1):
        chapters.append({"index": i, "title": act if isinstance(act, str) else str(act)})

    trust_checks = (quality_report.get("sections") or {}).get("trust_and_safety") or []
    package = {
        "project_id": ctx.project["project_id"],
        "video": video_entry["relative_path"],
        "video_checksum": video_entry.get("checksum"),
        "thumbnail": thumbnail_entry["relative_path"] if thumbnail_entry else None,
        "title": title,
        "title_alternatives": titles[1:5],
        "description": "\n\n".join(description_parts),
        "tags": strategy.get("tags") or [],
        "chapters": chapters,
        "subtitles": "burned_in",
        "visibility": "private",
        "ai_content_disclosure_required": True,
        "copyright_check": [
            {"rule_id": c["rule_id"], "status": c["status"], "evidence": c["evidence"]}
            for c in trust_checks
        ],
        "quality_gate_result": quality_report.get("result"),
        "created_at": _now_iso(),
        "note": "업로드는 수행하지 않는다 — PUBLISH_APPROVAL 승인 후 사람이 직접 업로드한다.",
    }
    if not package["tags"]:
        warnings.append("태그 비어 있음 — 게시 승인 전 채우세요")
    output_rel = "package/upload_package.json"
    write_json(ctx.project_path / output_rel, package)
    return ExecutorResult(status="COMPLETED",
                          outputs={"upload_package": output_rel}, warnings=warnings)


# ---------------------------------------------------------------------------
# 기본 registry 구성
# ---------------------------------------------------------------------------
def build_default_registry() -> ExecutorRegistry:
    registry = ExecutorRegistry()
    registry.register("project.intake", intake_executor)
    for name in CREATIVE_SPECS:
        registry.register(name, creative_workflow_executor)
    for name in ("approval.concept", "approval.script", "approval.assets", "approval.publish"):
        registry.register(name, human_gate_executor)
    registry.register("provider.asset_production", provider_job_executor)
    registry.register("longform.composition", composition_executor)
    registry.register("longform.quality_safety", quality_safety_executor)
    registry.register("longform.package", package_executor)
    return registry
