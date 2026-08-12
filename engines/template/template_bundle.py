# -*- coding: utf-8 -*-
"""Template bundle — production 템플릿 번들 로드/검증/스냅샷.

템플릿 폴더는 template.yaml 외에 pipeline/project_form/project_view/roles/quality
파일을 가질 수 있다. 기존 최소 템플릿(template.yaml만)은 계속 로드되지만,
production 프로젝트로 실행하려면 전체 번들 검증을 통과해야 한다.

executor 이름은 코드의 allowlist(ExecutorRegistry)에 등록된 이름만 허용한다.
YAML에서 임의의 Python 모듈/클래스를 import하지 않는다.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from core import ADOSFileNotFoundError, ADOSValidationError, load_yaml, write_json

# 번들 파일 참조 필드 → 기본 파일명
BUNDLE_FILE_FIELDS = {
    "pipeline_file": "pipeline.yaml",
    "project_form_file": "project_form.yaml",
    "project_view_file": "project_view.yaml",
    "roles_file": "roles.yaml",
    "quality_file": "quality.yaml",
}

ALLOWED_STEP_KINDS = [
    "creative_workflow",
    "deterministic",
    "provider_job",
    "human_gate",
    "quality_gate",
    "package",
]

STAGE_REQUIRED_FIELDS = [
    "id", "title", "kind", "owner_role", "executor",
    "requires", "produces", "depends_on",
]

PIPELINE_SNAPSHOT_REL = Path("workflow") / "pipeline_snapshot.json"
BUNDLE_SNAPSHOT_REL = Path("workflow") / "template_bundle_snapshot.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(data) -> str:
    """dict를 정렬된 JSON으로 직렬화해 sha256 해시를 만든다."""
    blob = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class TemplateBundle:
    """로드된 번들 데이터 컨테이너."""

    def __init__(self, template_id: str, metadata: dict, pipeline: dict | None,
                 project_form: dict | None, project_view: dict | None,
                 roles: dict | None, quality: dict | None):
        self.template_id = template_id
        self.metadata = metadata
        self.pipeline = pipeline
        self.project_form = project_form
        self.project_view = project_view
        self.roles = roles
        self.quality = quality

    @property
    def is_production_bundle(self) -> bool:
        return all(
            part is not None
            for part in (self.pipeline, self.project_form, self.project_view,
                         self.roles, self.quality)
        )

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "template": self.metadata,
            "pipeline": self.pipeline,
            "project_form": self.project_form,
            "project_view": self.project_view,
            "roles": self.roles,
            "quality": self.quality,
        }


def load_bundle_from_dir(template_dir: str | Path, metadata: dict) -> TemplateBundle:
    """template.yaml 메타데이터의 참조 필드를 따라 번들 파일들을 로드한다.

    참조 필드가 없는 파일은 None으로 둔다(최소 템플릿 호환).
    참조 필드가 있는데 파일이 없으면 에러.
    """
    template_dir = Path(template_dir)
    template_id = metadata["template_id"]
    parts = {}
    for field, _default in BUNDLE_FILE_FIELDS.items():
        filename = metadata.get(field)
        if not filename:
            parts[field] = None
            continue
        path = template_dir / filename
        if not path.is_file():
            raise ADOSFileNotFoundError(
                f"template.yaml이 참조하는 파일이 없습니다: {field}={filename}",
                location="template_bundle.load_bundle_from_dir",
                suggested_fix=f"{template_dir / filename} 파일을 생성하거나 참조를 제거하세요.",
            )
        parts[field] = load_yaml(path)
    return TemplateBundle(
        template_id=template_id,
        metadata=metadata,
        pipeline=parts["pipeline_file"],
        project_form=parts["project_form_file"],
        project_view=parts["project_view_file"],
        roles=parts["roles_file"],
        quality=parts["quality_file"],
    )


def _quality_rule_ids(quality: dict) -> set[str]:
    ids = set()
    for section in (quality.get("quality_rules") or {}).values():
        for rule in section or []:
            if isinstance(rule, dict) and rule.get("rule_id"):
                ids.add(rule["rule_id"])
    return ids


def validate_bundle(bundle: TemplateBundle, executor_allowlist: list[str]) -> list[str]:
    """production 번들 전체 검증. 문제 목록이 비어 있으면 통과.

    검증 실패 항목을 전부 모아 반환한다 (하나씩 고치는 왕복을 줄이기 위해).
    """
    problems: list[str] = []
    meta = bundle.metadata

    if not bundle.is_production_bundle:
        missing = [
            field for field, part in (
                ("pipeline_file", bundle.pipeline),
                ("project_form_file", bundle.project_form),
                ("project_view_file", bundle.project_view),
                ("roles_file", bundle.roles),
                ("quality_file", bundle.quality),
            ) if part is None
        ]
        problems.append(f"production 번들 파일 참조 누락: {', '.join(missing)}")
        return problems  # 이후 검증은 번들 파일 전제

    if meta.get("template_id") != bundle.template_id:
        problems.append(
            f"template_id 불일치: 폴더={bundle.template_id}, yaml={meta.get('template_id')}"
        )
    if not meta.get("content_type"):
        problems.append("content_type 누락 (template.yaml)")

    pipeline = bundle.pipeline
    stages = pipeline.get("stages") or []
    if not pipeline.get("pipeline_id"):
        problems.append("pipeline_id 누락 (pipeline.yaml)")
    if not stages:
        problems.append("stages가 비어 있습니다 (pipeline.yaml)")

    role_ids = {r.get("role_id") for r in (bundle.roles.get("roles") or [])}
    quality_ids = _quality_rule_ids(bundle.quality)

    seen_ids: set[str] = set()
    produced_keys: dict[str, str] = {}  # artifact_key -> stage_id
    stage_ids_in_order: list[str] = []

    for stage in stages:
        sid = stage.get("id", "<no-id>")
        for field in STAGE_REQUIRED_FIELDS:
            if field not in stage:
                problems.append(f"stage {sid}: 필수 필드 누락 '{field}'")
        if sid in seen_ids:
            problems.append(f"stage ID 중복: {sid}")
        seen_ids.add(sid)
        stage_ids_in_order.append(sid)

        kind = stage.get("kind")
        if kind not in ALLOWED_STEP_KINDS:
            problems.append(f"stage {sid}: 알 수 없는 kind '{kind}'")
        executor = stage.get("executor")
        if executor not in executor_allowlist:
            problems.append(f"stage {sid}: 알 수 없는 executor '{executor}'")
        owner = stage.get("owner_role")
        if owner not in role_ids:
            problems.append(f"stage {sid}: 존재하지 않는 role 참조 '{owner}'")
        for key in stage.get("produces") or []:
            if key in produced_keys:
                problems.append(
                    f"stage {sid}: artifact key 중복 '{key}' (먼저 {produced_keys[key]}가 생산)"
                )
            produced_keys[key] = sid
        for rule_id in stage.get("quality_rules") or []:
            if rule_id not in quality_ids:
                problems.append(f"stage {sid}: 존재하지 않는 quality rule 참조 '{rule_id}'")

    # dependency 검증 (존재 + 앞선 단계만 + 순환 금지)
    stage_index = {sid: i for i, sid in enumerate(stage_ids_in_order)}
    graph: dict[str, list[str]] = {}
    for stage in stages:
        sid = stage.get("id", "<no-id>")
        deps = stage.get("depends_on") or []
        graph[sid] = list(deps)
        for dep in deps:
            if dep not in stage_index:
                problems.append(f"stage {sid}: 잘못된 dependency '{dep}' (존재하지 않음)")

    # 순환 감지 (DFS)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {sid: WHITE for sid in graph}

    def visit(node: str, path: list[str]) -> None:
        color[node] = GRAY
        for dep in graph.get(node, []):
            if dep not in color:
                continue
            if color[dep] == GRAY:
                problems.append(f"순환 dependency: {' -> '.join(path + [node, dep])}")
            elif color[dep] == WHITE:
                visit(dep, path + [node])
        color[node] = BLACK

    for sid in graph:
        if color[sid] == WHITE:
            visit(sid, [])

    # requires artifact가 앞선 단계의 produces에 있는지
    available: set[str] = set()
    for stage in stages:
        sid = stage.get("id", "<no-id>")
        for key in stage.get("requires") or []:
            if key not in available:
                problems.append(
                    f"stage {sid}: requires '{key}'를 생산하는 앞선 단계가 없습니다"
                )
        for key in stage.get("produces") or []:
            available.add(key)

    # project_view 참조 검증
    view = bundle.project_view
    for tab in view.get("tabs") or []:
        tab_id = tab.get("id", "<no-id>")
        for sid in tab.get("stages") or []:
            if sid not in seen_ids:
                problems.append(f"project_view 탭 {tab_id}: 존재하지 않는 stage 참조 '{sid}'")
        for key in tab.get("artifacts") or []:
            if key not in produced_keys:
                problems.append(f"project_view 탭 {tab_id}: 존재하지 않는 artifact 참조 '{key}'")

    # duration 설정 검증
    recommended = meta.get("recommended_duration_seconds") or {}
    allowed = meta.get("allowed_duration_seconds") or {}
    if not isinstance(recommended, dict) or "min" not in recommended or "max" not in recommended:
        problems.append("recommended_duration_seconds에 min/max가 필요합니다 (template.yaml)")
    if not isinstance(allowed, dict) or "max" not in allowed:
        problems.append("allowed_duration_seconds에 max가 필요합니다 (template.yaml)")

    return problems


def snapshot_bundle(bundle: TemplateBundle, project_path: str | Path) -> dict:
    """검증된 번들을 프로젝트 폴더에 snapshot한다.

    이후 템플릿 원본이 변경되어도 진행 중인 프로젝트에는 영향이 없다.
    """
    project_path = Path(project_path)
    pipeline_snapshot = {
        "template_id": bundle.template_id,
        "template_version": str(
            bundle.metadata.get("template_version") or bundle.metadata.get("version")
        ),
        "pipeline_id": bundle.pipeline.get("pipeline_id"),
        "pipeline_version": str(bundle.pipeline.get("pipeline_version")),
        "stages": bundle.pipeline.get("stages"),
        "created_at": _now_iso(),
    }
    pipeline_snapshot["snapshot_hash"] = canonical_hash(
        {"stages": pipeline_snapshot["stages"], "pipeline_id": pipeline_snapshot["pipeline_id"]}
    )
    write_json(project_path / PIPELINE_SNAPSHOT_REL, pipeline_snapshot)

    bundle_snapshot = bundle.to_dict()
    bundle_snapshot["snapshot_created_at"] = _now_iso()
    bundle_snapshot["snapshot_hash"] = canonical_hash(bundle.to_dict())
    write_json(project_path / BUNDLE_SNAPSHOT_REL, bundle_snapshot)

    return {
        "pipeline_snapshot_ref": str(PIPELINE_SNAPSHOT_REL).replace("\\", "/"),
        "pipeline_snapshot_hash": pipeline_snapshot["snapshot_hash"],
        "template_snapshot_ref": str(BUNDLE_SNAPSHOT_REL).replace("\\", "/"),
        "pipeline_id": pipeline_snapshot["pipeline_id"],
        "pipeline_version": pipeline_snapshot["pipeline_version"],
        "template_version": pipeline_snapshot["template_version"],
    }


def raise_if_invalid(bundle: TemplateBundle, executor_allowlist: list[str]) -> None:
    problems = validate_bundle(bundle, executor_allowlist)
    if problems:
        raise ADOSValidationError(
            f"template bundle 검증 실패 ({len(problems)}건): " + " | ".join(problems),
            location="template_bundle.raise_if_invalid",
            suggested_fix="템플릿 번들 파일들을 스키마에 맞게 수정하세요.",
        )
