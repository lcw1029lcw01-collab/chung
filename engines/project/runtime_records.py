# -*- coding: utf-8 -*-
"""Runtime records — 비용 원장(cost ledger)과 감사 이벤트 로그(event log).

둘 다 append-only JSONL이다.
- 현재 가격을 코드에 하드코딩하지 않는다. 가격을 모르면 null + UNKNOWN.
- API key, token, 전체 프롬프트 같은 민감 정보는 기록하지 않는다.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from core import ensure_directory

COST_LEDGER_REL = Path("runtime") / "cost_ledger.jsonl"
EVENTS_REL = Path("runtime") / "events.jsonl"

COST_STATUSES = ["ESTIMATED", "INCURRED", "UNKNOWN", "CANCELLED"]

# 이벤트에 실수로 들어가면 안 되는 민감 키 (기록 전 제거)
_SENSITIVE_KEYS = {"api_key", "token", "authorization", "password", "secret", "prompt_full"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, record: dict) -> None:
    ensure_directory(path.parent)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def _strip_sensitive(data: dict | None) -> dict:
    if not data:
        return {}
    return {k: v for k, v in data.items() if k.lower() not in _SENSITIVE_KEYS}


class CostLedger:
    def __init__(self, project_path: str | Path, project_id: str | None = None):
        self.project_path = Path(project_path)
        self.path = self.project_path / COST_LEDGER_REL
        self.project_id = project_id

    def append(
        self,
        stage_id: str,
        provider: str,
        model_or_tool: str | None = None,
        job_id: str | None = None,
        estimated_cost: float | None = None,
        actual_cost: float | None = None,
        currency: str | None = None,
        units: str | None = None,
        status: str = "UNKNOWN",
    ) -> dict:
        if status not in COST_STATUSES:
            status = "UNKNOWN"
        # 가격 미상이면 null + UNKNOWN 통화로 남긴다 — 숫자 조작 금지
        record = {
            "timestamp": _now_iso(),
            "project_id": self.project_id,
            "stage_id": stage_id,
            "provider": provider,
            "model_or_tool": model_or_tool,
            "job_id": job_id,
            "estimated_cost": estimated_cost,
            "actual_cost": actual_cost,
            "currency": currency or "UNKNOWN",
            "units": units,
            "status": status,
        }
        _append_jsonl(self.path, record)
        return record

    def entries(self) -> list[dict]:
        return _read_jsonl(self.path)

    def summary(self) -> dict:
        entries = self.entries()
        total_actual = 0.0
        unknown = 0
        currencies = set()
        for e in entries:
            if e.get("actual_cost") is not None:
                total_actual += float(e["actual_cost"])
                currencies.add(e.get("currency") or "UNKNOWN")
            else:
                unknown += 1
        return {
            "entry_count": len(entries),
            "total_actual": total_actual if total_actual else None,
            "currencies": sorted(currencies),
            "unknown_cost_entries": unknown,
        }


class EventLog:
    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path)
        self.path = self.project_path / EVENTS_REL

    def append(
        self,
        event_type: str,
        stage_id: str | None = None,
        actor_type: str = "system",
        actor_id: str = "ados",
        previous_status: str | None = None,
        new_status: str | None = None,
        message: str = "",
        metadata: dict | None = None,
    ) -> dict:
        record = {
            "timestamp": _now_iso(),
            "event_type": event_type,
            "stage_id": stage_id,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "previous_status": previous_status,
            "new_status": new_status,
            "message": message,
            "metadata": _strip_sensitive(metadata),
        }
        _append_jsonl(self.path, record)
        return record

    def entries(self) -> list[dict]:
        return _read_jsonl(self.path)
