# -*- coding: utf-8 -*-
"""ADOS common constants and types.

근거 문서:
- ProjectStatus: docs/07_PROJECT_SPEC.md #4~5
- StageName: docs/15_WORKFLOW_ORCHESTRATOR.md #5
- QualityGateResult: docs/26_QUALITY_ENGINE.md #9
- ProviderMode: docs/14_PROVIDER_ENGINE.md #7
"""
from enum import StrEnum


class ProjectStatus(StrEnum):
    NEW = "NEW"
    INITIALIZED = "INITIALIZED"
    RESEARCH = "RESEARCH"
    KNOWLEDGE = "KNOWLEDGE"
    STORY = "STORY"
    DIRECTION = "DIRECTION"
    TIMELINE = "TIMELINE"
    VISUAL = "VISUAL"
    MOTION = "MOTION"
    VOICE = "VOICE"
    SUBTITLE = "SUBTITLE"
    EDITING = "EDITING"
    QUALITY = "QUALITY"
    AUTO_FIX = "AUTO_FIX"
    PACKAGE = "PACKAGE"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    ANALYTICS = "ANALYTICS"
    LEARNING = "LEARNING"
    COMPLETE = "COMPLETE"


class StageName(StrEnum):
    INITIALIZED = "INITIALIZED"
    RESEARCH = "RESEARCH"
    KNOWLEDGE = "KNOWLEDGE"
    STORY = "STORY"
    DIRECTION = "DIRECTION"
    TIMELINE = "TIMELINE"
    VISUAL = "VISUAL"
    MOTION = "MOTION"
    VOICE = "VOICE"
    SUBTITLE = "SUBTITLE"
    EDITING = "EDITING"
    QUALITY = "QUALITY"
    AUTO_FIX = "AUTO_FIX"
    PACKAGE = "PACKAGE"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    ANALYTICS = "ANALYTICS"
    LEARNING = "LEARNING"
    AI_EVOLUTION = "AI_EVOLUTION"
    COMPLETE = "COMPLETE"


# 전체 워크플로우 라이프사이클 순서
# (docs/15_WORKFLOW_ORCHESTRATOR.md #5 + 28~31 후속 단계.
#  AUTO_FIX는 Quality 결과에 따라 조건부로 실행된다.)
STAGE_ORDER: list[StageName] = [
    StageName.INITIALIZED,
    StageName.RESEARCH,
    StageName.KNOWLEDGE,
    StageName.STORY,
    StageName.DIRECTION,
    StageName.TIMELINE,
    StageName.VISUAL,
    StageName.MOTION,
    StageName.VOICE,
    StageName.SUBTITLE,
    StageName.EDITING,
    StageName.QUALITY,
    StageName.AUTO_FIX,
    StageName.PACKAGE,
    StageName.READY,
    StageName.PUBLISHED,
    StageName.ANALYTICS,
    StageName.LEARNING,
    StageName.AI_EVOLUTION,
    StageName.COMPLETE,
]


class QualityGateResult(StrEnum):
    PASS = "PASS"
    HUMAN_REVIEW_RECOMMENDED = "HUMAN_REVIEW_RECOMMENDED"
    AUTO_FIX_REQUIRED = "AUTO_FIX_REQUIRED"
    PARTIAL_REGENERATION_REQUIRED = "PARTIAL_REGENERATION_REQUIRED"
    FAIL = "FAIL"


class ProviderMode(StrEnum):
    MANUAL = "manual"
    SEMI_AUTOMATED = "semi_automated"
    AUTOMATED = "automated"


class RunMode(StrEnum):
    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    AUTO_UNTIL_QUALITY = "auto_until_quality"
    AUTO_UNTIL_PACKAGE = "auto_until_package"
    FULL_AUTO = "full_auto"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
