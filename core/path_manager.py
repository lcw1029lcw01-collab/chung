# -*- coding: utf-8 -*-
"""ADOS project path manager.

프로젝트 루트를 찾고, 루트 밖으로 나가지 않는 안전한 경로 결합을 제공한다.
폴더 책임: docs/02_DEVELOPMENT_RULES.md #6
"""
from pathlib import Path

from .errors import ADOSConfigError, ADOSValidationError

# 프로젝트 루트 판별 기준: 이 두 가지가 모두 존재해야 한다.
_ROOT_MARKERS = ("docs", "config")


class ADOSPathManager:
    def __init__(self, root: str | Path | None = None):
        if root is not None:
            self.root = Path(root).resolve()
            if not self._is_project_root(self.root):
                raise ADOSConfigError(
                    f"지정한 경로가 ADOS 프로젝트 루트가 아닙니다: {self.root}",
                    location="ADOSPathManager.__init__",
                    suggested_fix="docs/와 config/가 있는 프로젝트 루트를 지정하세요.",
                )
        else:
            self.root = self.find_project_root()

    @staticmethod
    def _is_project_root(path: Path) -> bool:
        return all((path / m).is_dir() for m in _ROOT_MARKERS)

    @classmethod
    def find_project_root(cls, start: str | Path | None = None) -> Path:
        """start(기본: cwd)에서 위로 올라가며 프로젝트 루트를 찾는다."""
        current = Path(start or Path.cwd()).resolve()
        for candidate in (current, *current.parents):
            if cls._is_project_root(candidate):
                return candidate
        raise ADOSConfigError(
            f"ADOS 프로젝트 루트를 찾을 수 없습니다 (시작 위치: {current})",
            location="ADOSPathManager.find_project_root",
            suggested_fix="프로젝트 폴더 안에서 실행하거나 root를 직접 지정하세요.",
        )

    def join(self, *parts: str | Path) -> Path:
        """루트 기준 경로 결합. 결과가 루트 밖이면 에러."""
        joined = (self.root.joinpath(*parts)).resolve()
        if joined != self.root and self.root not in joined.parents:
            raise ADOSValidationError(
                f"경로가 프로젝트 루트를 벗어납니다: {joined}",
                location="ADOSPathManager.join",
                cause=f"parts={parts}",
                suggested_fix="상대 경로에 '..' 등 루트 탈출 요소를 넣지 마세요.",
            )
        return joined

    # --- common path helpers ---
    @property
    def docs(self) -> Path:
        return self.root / "docs"

    @property
    def templates(self) -> Path:
        return self.root / "templates"

    @property
    def channels(self) -> Path:
        return self.root / "channels"

    @property
    def projects(self) -> Path:
        return self.root / "projects"

    @property
    def engines(self) -> Path:
        return self.root / "engines"

    @property
    def providers(self) -> Path:
        return self.root / "providers"

    @property
    def memory(self) -> Path:
        return self.root / "memory"

    @property
    def config(self) -> Path:
        return self.root / "config"

    @property
    def prompts(self) -> Path:
        return self.root / "prompts"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    @property
    def reports(self) -> Path:
        return self.root / "reports"

    @property
    def outputs(self) -> Path:
        return self.root / "outputs"
