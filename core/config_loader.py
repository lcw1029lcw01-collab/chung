# -*- coding: utf-8 -*-
"""ADOS config loader.

config/ados.yaml, config/providers.yaml, config/quality.yaml을 로드하고
간단한 getter를 제공한다.
"""
from .errors import ADOSConfigError
from .file_loader import load_yaml
from .path_manager import ADOSPathManager
from .validator import ADOSValidator

ADOS_REQUIRED_FIELDS = [
    "company_name",
    "system_name",
    "version",
    "default_language",
    "supported_languages",
    "default_run_mode",
    "human_review_required",
]

QUALITY_REQUIRED_THRESHOLDS = [
    "pass",
    "human_review_recommended",
    "auto_fix_required",
    "partial_regeneration_required",
    "fail",
]


class ADOSConfigLoader:
    def __init__(self, path_manager: ADOSPathManager | None = None):
        self.paths = path_manager or ADOSPathManager()
        self.ados = self._load("ados.yaml")
        self.providers_config = self._load("providers.yaml")
        self.quality = self._load("quality.yaml")
        self._validate()

    def _load(self, filename: str) -> dict:
        data = load_yaml(self.paths.config / filename)
        if not isinstance(data, dict):
            raise ADOSConfigError(
                f"config/{filename}의 최상위는 dict여야 합니다.",
                location="ADOSConfigLoader._load",
            )
        return data

    def _validate(self) -> None:
        ADOSValidator.require_fields(
            self.ados, ADOS_REQUIRED_FIELDS, location="config/ados.yaml"
        )
        ADOSValidator.require_fields(
            self.providers_config, ["providers"], location="config/providers.yaml"
        )
        ADOSValidator.require_fields(
            self.quality, ["quality_thresholds"], location="config/quality.yaml"
        )
        ADOSValidator.require_fields(
            self.quality["quality_thresholds"],
            QUALITY_REQUIRED_THRESHOLDS,
            location="config/quality.yaml:quality_thresholds",
        )

    # --- ados.yaml getters ---
    @property
    def company_name(self) -> str:
        return self.ados["company_name"]

    @property
    def system_name(self) -> str:
        return self.ados["system_name"]

    @property
    def version(self) -> str:
        return str(self.ados["version"])

    @property
    def default_language(self) -> str:
        return self.ados["default_language"]

    @property
    def supported_languages(self) -> list[str]:
        return list(self.ados["supported_languages"])

    @property
    def default_run_mode(self) -> str:
        return self.ados["default_run_mode"]

    @property
    def human_review_required(self) -> bool:
        return bool(self.ados["human_review_required"])

    # --- providers.yaml getters ---
    @property
    def providers(self) -> dict:
        return self.providers_config["providers"]

    def get_provider(self, role: str) -> dict:
        """role 예: visual, motion, voice, subtitle, editing"""
        providers = self.providers
        if role not in providers:
            raise ADOSConfigError(
                f"정의되지 않은 provider role: {role}",
                location="ADOSConfigLoader.get_provider",
                suggested_fix=f"config/providers.yaml에 '{role}'을 추가하세요.",
            )
        return providers[role]

    # --- quality.yaml getters ---
    @property
    def quality_thresholds(self) -> dict:
        return self.quality["quality_thresholds"]

    def get_quality_threshold(self, name: str) -> int:
        thresholds = self.quality_thresholds
        if name not in thresholds:
            raise ADOSConfigError(
                f"정의되지 않은 quality threshold: {name}",
                location="ADOSConfigLoader.get_quality_threshold",
                suggested_fix=f"config/quality.yaml에 '{name}'을 추가하세요.",
            )
        return int(thresholds[name])
