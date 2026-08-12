# -*- coding: utf-8 -*-
"""Executor registry — executor 이름과 Python handler를 연결하는 명시적 allowlist.

YAML 문자열로 임의의 Python 모듈/클래스를 import하지 않는다.
pipeline.yaml의 executor 필드는 반드시 여기 등록된 이름만 사용할 수 있다.

각 executor는 공통 결과 형식(ExecutorResult)을 반환한다:
  status / outputs / blockers / warnings / metrics / cost / external_call_made
"""
from dataclasses import dataclass, field
from pathlib import Path

from core import ADOSValidationError

# 코드 allowlist — 템플릿 검증은 이 목록만 신뢰한다.
EXECUTOR_ALLOWLIST = [
    "project.intake",
    "longform.opportunity_research",
    "longform.strategy",
    "approval.concept",
    "longform.evidence_research",
    "longform.script",
    "approval.script",
    "longform.direction",
    "longform.asset_plan",
    "provider.asset_production",
    "approval.assets",
    "longform.composition",
    "longform.quality_safety",
    "longform.package",
    "approval.publish",
]

# executor 결과 status — step 상태로 그대로 반영 가능한 값만 허용
RESULT_STATUSES = [
    "COMPLETED",
    "WAITING_INPUT",
    "WAITING_EXTERNAL",
    "WAITING_APPROVAL",
    "FAILED",
    "BLOCKED",
]

# production 산출물로 통과시키지 않는 placeholder 마커 (소문자 비교)
PLACEHOLDER_MARKERS = [
    "placeholder",
    "dummy",
    "lorem ipsum",
    "sample disclaimer",
    "샘플입니다",
    "더미",
    "tbd",
    "todo:",
]


@dataclass
class ExecutorResult:
    status: str
    outputs: dict = field(default_factory=dict)      # artifact_key -> 프로젝트 상대 경로
    blockers: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    cost: dict | None = None                         # {provider, estimated_cost, ...}
    external_call_made: bool = False

    def __post_init__(self):
        if self.status not in RESULT_STATUSES:
            raise ADOSValidationError(
                f"허용되지 않는 executor status: {self.status}",
                location="ExecutorResult",
            )


@dataclass
class ExecutionContext:
    """executor에 전달되는 실행 컨텍스트."""
    project_path: Path
    root: Path                      # ADOS 저장소 루트
    project: dict                   # project.json
    stage: dict                     # pipeline snapshot의 stage 정의
    pipeline: dict                  # pipeline snapshot 전체
    state: dict                     # workflow state (읽기 전용으로 취급)
    artifacts: object               # ArtifactIndex
    costs: object                   # CostLedger
    events: object                  # EventLog
    allow_external: bool = False
    force: bool = False
    imported_result: dict | None = None      # import-result로 들어온 데이터
    imported_result_ref: str | None = None   # 원본 결과 파일 경로(기록용)
    bundle: dict | None = None               # template bundle snapshot (dict)


def scan_for_placeholders(data) -> list[str]:
    """결과 데이터 안의 placeholder/dummy 마커를 찾아 위치 목록을 반환한다."""
    hits: list[str] = []

    def walk(node, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else str(key))
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")
        elif isinstance(node, str):
            lowered = node.lower()
            for marker in PLACEHOLDER_MARKERS:
                if marker in lowered:
                    hits.append(f"{path}: '{marker}'")
                    break

    walk(data, "")
    return hits


class ExecutorRegistry:
    """executor 이름 → handler 매핑. handler(ctx) -> ExecutorResult."""

    def __init__(self):
        self._handlers: dict[str, callable] = {}

    def register(self, name: str, handler) -> None:
        if name not in EXECUTOR_ALLOWLIST:
            raise ADOSValidationError(
                f"allowlist에 없는 executor는 등록할 수 없습니다: {name}",
                location="ExecutorRegistry.register",
                suggested_fix="EXECUTOR_ALLOWLIST에 이름을 추가한 뒤 등록하세요.",
            )
        self._handlers[name] = handler

    def get(self, name: str):
        if name not in self._handlers:
            raise ADOSValidationError(
                f"등록되지 않은 executor: {name}",
                location="ExecutorRegistry.get",
                suggested_fix="engines/workflow/executors.py의 기본 registry를 사용하거나 handler를 등록하세요.",
            )
        return self._handlers[name]

    def names(self) -> list[str]:
        return sorted(self._handlers)

    def has(self, name: str) -> bool:
        return name in self._handlers
