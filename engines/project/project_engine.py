# -*- coding: utf-8 -*-
"""Project engine.

projects/{channel_id}/{year}/{month}/{project_id}/ 아래에
project.json, topic.json과 표준 하위 폴더를 만든다.

- Project ID 규칙: docs/07_PROJECT_SPEC.md #7 (YYYYMMDD-HHMMSS-{channel_id}-{topic_slug})
- project.json / topic.json 최소 형태: docs/07_PROJECT_SPEC.md #9~10

production_mode 요청이면 채널의 template bundle을 검증·snapshot하고
workflow/runtime/ui 파일을 함께 생성한다. production_mode가 없는 기존 호출은
이전과 동일하게 동작한다 (레거시 데모/테스트 호환).
"""
import re
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from core import (
    ADOSFileNotFoundError,
    ADOSLogger,
    ADOSPathManager,
    ADOSValidationError,
    ADOSValidator,
    ProjectStatus,
    StageName,
    ensure_directory,
    load_json,
    load_yaml,
    write_json,
)
from engines.template import TemplateLoader
from engines.template.template_bundle import snapshot_bundle as _snapshot_bundle

PROJECT_REQUEST_FIELDS = ["channel_id", "topic", "target_languages", "duration_seconds"]

PRODUCTION_SUBFOLDERS = [
    "runtime",
    "ui",
    "workflow/work_orders",
    "workflow/approvals",
    "assets/video",
    "assets/production",
]

_FORM_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
}

PROJECT_SUBFOLDERS = [
    "research",
    "knowledge",
    "story",
    "direction",
    "timeline",
    "prompts",
    "assets",
    "assets/images",
    "assets/motion",
    "assets/audio",
    "assets/subtitles",
    "edit",
    "reports",
    "workflow",
    "workflow/handoffs",
    "workflow/stage_results",
    "logs",
    "package",
    "analytics",
    "learning",
    "ai_evolution",
]

_MAX_SLUG_WORDS = 8


def make_topic_slug(topic: str) -> str:
    """소문자, 공백/특수문자 금지, 5~8단어 축약 (docs/07 #7)."""
    ascii_only = re.sub(r"[^a-zA-Z0-9\s-]", " ", topic)
    words = [w for w in re.split(r"[\s-]+", ascii_only.lower()) if w]
    if not words:
        return "topic"
    return "-".join(words[:_MAX_SLUG_WORDS])


class ProjectEngine:
    def __init__(self, path_manager: ADOSPathManager | None = None, logger: ADOSLogger | None = None):
        self.paths = path_manager or ADOSPathManager()
        self.logger = logger

    def _resolve_timezone(self):
        """config/ados.yaml의 timezone을 사용한다.

        config가 없거나(테스트 임시 루트 등) 시스템에 tz 데이터가 없어
        ZoneInfo 로드가 실패하면 UTC로 동작한다.
        """
        try:
            config = load_yaml(self.paths.config / "ados.yaml")
            tz_name = config.get("timezone") if isinstance(config, dict) else None
            if tz_name:
                return ZoneInfo(tz_name)
        except Exception:
            pass
        return timezone.utc

    def create_project(self, request: dict) -> dict:
        ADOSValidator.require_fields(
            request, PROJECT_REQUEST_FIELDS, location="ProjectEngine.create_project"
        )
        channel_id = request["channel_id"]

        channel_yaml = self.paths.channels / channel_id / "channel.yaml"
        if not channel_yaml.is_file():
            raise ADOSFileNotFoundError(
                f"채널이 존재하지 않습니다: {channel_id}",
                location="ProjectEngine.create_project",
                suggested_fix="ChannelEngine.create_channel로 채널을 먼저 생성하세요.",
            )
        channel = load_yaml(channel_yaml)

        # production 준비 — 폴더를 만들기 전에 번들 검증·입력 검증을 끝낸다
        production_mode = bool(request.get("production_mode"))
        bundle = None
        validated_inputs: dict | None = None
        input_warnings: list[str] = []
        if production_mode:
            template_id = channel.get("template_id")
            if not template_id:
                raise ADOSValidationError(
                    f"채널에 template_id가 없습니다: {channel_id}",
                    location="ProjectEngine.create_project",
                )
            bundle = TemplateLoader(self.paths).load_validated_bundle(template_id)
            validated_inputs, input_warnings = self._validate_project_inputs(bundle, request)

        now = datetime.now(self._resolve_timezone())
        # topic_slug가 오면 그것을 정제해 사용, 없으면 topic에서 생성 (기존 동작)
        slug = make_topic_slug(request.get("topic_slug") or request["topic"])
        project_id = f"{now:%Y%m%d}-{now:%H%M%S}-{channel_id}-{slug}"

        base = self.paths.projects / channel_id / f"{now:%Y}" / f"{now:%m}"
        folder = base / project_id
        suffix = 2
        while folder.exists():  # 동일 시간 생성 충돌 시 suffix (docs/07 #7)
            folder = base / f"{project_id}-{suffix:02d}"
            suffix += 1
        project_id = folder.name

        for sub in PROJECT_SUBFOLDERS:
            ensure_directory(folder / sub)

        created_at = now.isoformat()
        project_data = {
            "project_id": project_id,
            "project_name": request["topic"],
            "version": "1.0.0",
            "status": str(ProjectStatus.INITIALIZED),
            "current_stage": str(StageName.RESEARCH),
            "created_at": created_at,
            "updated_at": created_at,
            "company": {"name": "CHUNG COMPANY", "system": "ADOS"},
            "channel": {
                "channel_id": channel_id,
                "channel_name": channel.get("channel_name", ""),
                "template_id": channel.get("template_id", ""),
                "template_version": channel.get("template_version", ""),
            },
            "topic": {
                "topic_id": slug,
                "topic_source": "USER",
                "title": request["topic"],
            },
            "languages": {
                "master_language": channel.get("language", "ko"),
                "target_languages": list(request["target_languages"]),
            },
            "duration": {"target_seconds": int(request["duration_seconds"])},
        }
        write_json(folder / "project.json", project_data)

        topic_data = {
            "topic_id": slug,
            "source": "USER",
            "title": request["topic"],
            "slug": slug,
            "category": channel_id,
            "keywords": [],
            "target_audience": [],
            "topic_score": None,
            "growth_notes": [],
            "risk_notes": [],
        }
        write_json(folder / "topic.json", topic_data)

        if production_mode:
            project_data = self._initialize_production_project(
                folder, project_data, bundle, validated_inputs, input_warnings, request
            )

        if self.logger:
            self.logger.info(
                f"프로젝트 생성: {project_id}",
                metadata={"project_id": project_id, "channel_id": channel_id,
                          "production_mode": production_mode},
            )
        return {"project_id": project_id, "path": str(folder), "project": project_data,
                "input_warnings": input_warnings}

    # --- production 지원 ---
    @staticmethod
    def _validate_project_inputs(bundle, request: dict) -> tuple[dict, list[str]]:
        """project_form 스키마로 입력을 검증하고 기본값을 채운다.

        권장 길이 밖이면 경고, hard maximum 초과만 실패.
        """
        inputs = dict(request.get("project_inputs") or {})
        inputs.setdefault("topic", request["topic"])
        inputs.setdefault("target_duration_seconds", int(request["duration_seconds"]))
        problems: list[str] = []
        for field_def in (bundle.project_form or {}).get("fields") or []:
            name = field_def["name"]
            if name not in inputs or inputs[name] is None:
                if field_def.get("default") is not None:
                    inputs[name] = field_def["default"]
                elif field_def.get("required"):
                    problems.append(f"필수 입력 누락: {name}")
                    continue
                else:
                    inputs.setdefault(name, None)
            value = inputs.get(name)
            if value is None:
                continue
            type_check = _FORM_TYPE_CHECKS.get(field_def.get("type", "string"))
            if type_check and not type_check(value):
                problems.append(f"입력 형식 오류: {name}={value!r} (기대: {field_def.get('type')})")
            enum = field_def.get("enum")
            if enum and value not in enum:
                problems.append(f"허용되지 않는 값: {name}={value!r} (허용: {', '.join(map(str, enum))})")
        if problems:
            raise ADOSValidationError(
                f"project_inputs 검증 실패: {'; '.join(problems)}",
                location="ProjectEngine._validate_project_inputs",
                suggested_fix="project_form.yaml의 필드 정의에 맞게 입력을 수정하세요.",
            )

        warnings: list[str] = []
        meta = bundle.metadata
        duration = inputs.get("target_duration_seconds")
        allowed = meta.get("allowed_duration_seconds") or {}
        recommended = meta.get("recommended_duration_seconds") or {}
        if isinstance(duration, (int, float)):
            max_allowed = allowed.get("max")
            if max_allowed and duration > max_allowed:
                raise ADOSValidationError(
                    f"목표 길이 {duration}s가 hard maximum {max_allowed}s를 초과합니다",
                    location="ProjectEngine._validate_project_inputs",
                    suggested_fix=f"{max_allowed}s 이하로 조정하세요.",
                )
            if recommended and not (
                recommended.get("min", 0) <= duration <= recommended.get("max", float("inf"))
            ):
                warnings.append(
                    f"목표 길이 {duration}s가 권장 범위 "
                    f"({recommended.get('min')}~{recommended.get('max')}s) 밖입니다"
                )
        return inputs, warnings

    def _initialize_production_project(
        self, folder: Path, project_data: dict, bundle,
        validated_inputs: dict, input_warnings: list[str], request: dict,
    ) -> dict:
        from engines.project.project_view_builder import ProjectViewBuilder
        from engines.project.runtime_records import EventLog
        from engines.workflow.production_workflow import create_production_workflow_state

        for sub in PRODUCTION_SUBFOLDERS:
            ensure_directory(folder / sub)

        # 번들 snapshot — 이후 템플릿 원본이 바뀌어도 이 프로젝트는 영향 없음
        snapshot_refs = _snapshot_bundle(bundle, folder)

        project_data.update({
            "template_id": bundle.template_id,
            "template_version": snapshot_refs["template_version"],
            "pipeline_id": snapshot_refs["pipeline_id"],
            "pipeline_version": snapshot_refs["pipeline_version"],
            "content_type": bundle.metadata.get("content_type"),
            "run_mode": request.get("run_mode", "manual"),
            "template_snapshot_ref": snapshot_refs["template_snapshot_ref"],
            "project_inputs": validated_inputs,
            "production_mode": True,
            "input_warnings": input_warnings,
        })
        write_json(folder / "project.json", project_data)

        pipeline_snapshot = load_json(folder / snapshot_refs["pipeline_snapshot_ref"])
        create_production_workflow_state(folder, project_data, snapshot_refs, pipeline_snapshot)

        write_json(folder / "runtime" / "artifact_index.json",
                   {"artifacts": {}, "updated_at": None})
        (folder / "runtime" / "cost_ledger.jsonl").touch()
        write_json(folder / "reports" / "decision_records.json", {"records": []})
        EventLog(folder).append(
            "PROJECT_CREATED",
            message=f"production project 생성 (template={bundle.template_id})",
            metadata={"warnings": input_warnings},
        )
        ProjectViewBuilder(folder).build()
        return project_data
