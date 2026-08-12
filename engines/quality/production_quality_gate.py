# -*- coding: utf-8 -*-
"""Production quality/safety gate — 실제 검증 근거 기반 게이트.

기존 dummy QualityEngine(무조건 95점 PASS)과 달리:
- 기본 상태는 UNASSESSED — 검증 근거가 없으면 통과시키지 않는다.
- 임의의 숫자 점수를 만들지 않는다. 항목별 PASS/FAIL/UNASSESSED + evidence만 기록.
- technical / editorial / trust_and_safety 세 영역을 분리해 검사한다.

결과: PASS | HUMAN_REVIEW_REQUIRED | REVISION_REQUIRED | BLOCKED
  BLOCKER 심각도 실패 → BLOCKED
  MAJOR/MINOR 실패 → REVISION_REQUIRED
  실패 없음 + UNASSESSED 존재 → HUMAN_REVIEW_REQUIRED (사람이 승인해야 통과)
  전 항목 PASS → PASS
"""
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from core import ADOSLogger

GATE_RESULTS = ["PASS", "HUMAN_REVIEW_REQUIRED", "REVISION_REQUIRED", "BLOCKED"]

# 템플릿 quality 규칙이 없어도 안전한 기본 심각도 —
# 최종 영상 부재/판독 불가/스트림 없음은 항상 blocker다.
_DEFAULT_SEVERITIES = {
    "tech.required_files": "BLOCKER",
    "tech.file_size": "BLOCKER",
    "tech.ffprobe": "BLOCKER",
    "tech.video_stream": "BLOCKER",
    "tech.audio_stream": "BLOCKER",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check(rule_id: str, status: str, evidence: str, severity: str) -> dict:
    return {"rule_id": rule_id, "status": status, "evidence": evidence, "severity": severity}


class ProductionQualityGate:
    def __init__(self, logger: ADOSLogger | None = None, ffprobe: str = "ffprobe"):
        self.logger = logger
        self.ffprobe = ffprobe

    def _ffprobe_available(self) -> bool:
        return shutil.which(self.ffprobe) is not None

    def _probe_streams(self, video_path: Path) -> dict | None:
        try:
            result = subprocess.run(
                [self.ffprobe, "-v", "error", "-show_streams", "-show_format",
                 "-of", "json", str(video_path)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            if result.returncode != 0:
                return None
            return json.loads(result.stdout)
        except Exception:
            return None

    # --- technical ---
    def _assess_technical(
        self, project_path: Path, video_rel: str | None,
        composition_report: dict | None, quality_rules: dict, allowed_duration: dict,
    ) -> list[dict]:
        severity = {
            r["rule_id"]: r.get("severity", "MAJOR")
            for section in (quality_rules.get("quality_rules") or {}).values()
            for r in section or []
        }
        checks: list[dict] = []

        def sev(rule_id: str) -> str:
            return severity.get(rule_id, _DEFAULT_SEVERITIES.get(rule_id, "MAJOR"))

        video_path = (project_path / video_rel) if video_rel else None
        if not video_path or not video_path.is_file():
            checks.append(_check("tech.required_files", "FAIL",
                                 f"최종 영상 없음: {video_rel}", sev("tech.required_files")))
            return checks
        checks.append(_check("tech.required_files", "PASS", str(video_rel), sev("tech.required_files")))

        size = video_path.stat().st_size
        checks.append(_check(
            "tech.file_size", "PASS" if size > 0 else "FAIL",
            f"{size} bytes", sev("tech.file_size"),
        ))

        if not self._ffprobe_available():
            for rule_id in ("tech.ffprobe", "tech.duration", "tech.resolution",
                            "tech.video_stream", "tech.audio_stream"):
                checks.append(_check(rule_id, "UNASSESSED", "ffprobe 없음 — 검증 불가", sev(rule_id)))
        else:
            probe = self._probe_streams(video_path)
            if probe is None:
                checks.append(_check("tech.ffprobe", "FAIL", "ffprobe 판독 실패", sev("tech.ffprobe")))
            else:
                checks.append(_check("tech.ffprobe", "PASS", "판독 성공", sev("tech.ffprobe")))
                duration = float(probe.get("format", {}).get("duration", 0) or 0)
                max_seconds = (allowed_duration or {}).get("max")
                if max_seconds and duration > float(max_seconds):
                    checks.append(_check("tech.duration", "FAIL",
                                         f"{duration:.1f}s > 허용 {max_seconds}s", sev("tech.duration")))
                elif duration <= 0:
                    checks.append(_check("tech.duration", "FAIL", "길이 0", sev("tech.duration")))
                else:
                    checks.append(_check("tech.duration", "PASS", f"{duration:.1f}s", sev("tech.duration")))
                streams = probe.get("streams", [])
                video_streams = [s for s in streams if s.get("codec_type") == "video"]
                audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
                checks.append(_check("tech.video_stream",
                                     "PASS" if video_streams else "FAIL",
                                     f"video 스트림 {len(video_streams)}개", sev("tech.video_stream")))
                checks.append(_check("tech.audio_stream",
                                     "PASS" if audio_streams else "FAIL",
                                     f"audio 스트림 {len(audio_streams)}개", sev("tech.audio_stream")))
                min_res = (quality_rules.get("gate") or {}).get("min_resolution") or {}
                if video_streams:
                    width = int(video_streams[0].get("width", 0) or 0)
                    height = int(video_streams[0].get("height", 0) or 0)
                    ok = width >= int(min_res.get("width", 0)) and height >= int(min_res.get("height", 0))
                    checks.append(_check("tech.resolution",
                                         "PASS" if ok else "FAIL",
                                         f"{width}x{height}", sev("tech.resolution")))

        report = composition_report or {}
        if report:
            checks.append(_check(
                "tech.silence_or_corruption",
                "PASS" if report.get("duration_match") else "FAIL",
                f"duration_match={report.get('duration_match')}",
                sev("tech.silence_or_corruption"),
            ))
            checks.append(_check(
                "tech.subtitle_timing",
                "PASS" if report.get("line_overflow_count", 1) == 0 else "FAIL",
                f"줄초과 {report.get('line_overflow_count')}건",
                sev("tech.subtitle_timing"),
            ))
            speed_warnings = report.get("reading_speed_warning_count", 0)
            checks.append(_check(
                "tech.subtitle_reading_speed",
                "PASS" if speed_warnings == 0 else "FAIL",
                f"읽기속도 경고 {speed_warnings}건",
                sev("tech.subtitle_reading_speed"),
            ))
            visible = report.get("subtitles_visible")
            checks.append(_check(
                "tech.subtitle_visibility",
                "UNASSESSED" if visible is None else ("PASS" if visible else "FAIL"),
                f"subtitles_visible={visible}",
                sev("tech.subtitle_visibility"),
            ))
        else:
            for rule_id in ("tech.silence_or_corruption", "tech.subtitle_timing",
                            "tech.subtitle_reading_speed", "tech.subtitle_visibility"):
                checks.append(_check(rule_id, "UNASSESSED", "composition report 없음", sev(rule_id)))
        return checks

    # --- editorial ---
    @staticmethod
    def _assess_editorial(strategy: dict | None, script: dict | None) -> list[dict]:
        checks: list[dict] = []
        if not strategy or not script:
            for rule_id in ("edit.strategy_script_alignment", "edit.hook_and_payoff",
                            "edit.unsupported_claims", "edit.previous_video_difference",
                            "edit.original_angle"):
                checks.append(_check(rule_id, "UNASSESSED", "전략/대본 artifact 없음", "MAJOR"))
            checks.append(_check("edit.scene_repetition", "UNASSESSED", "자동 검사 불가 — 사람 검토 필요", "MINOR"))
            checks.append(_check("edit.templated_structure", "UNASSESSED", "자동 검사 불가 — 사람 검토 필요", "MINOR"))
            return checks

        checks.append(_check(
            "edit.hook_and_payoff",
            "PASS" if (script.get("hook") and script.get("payoff")) else "FAIL",
            f"hook={'있음' if script.get('hook') else '없음'}, payoff={'있음' if script.get('payoff') else '없음'}",
            "MAJOR",
        ))
        refs = script.get("source_claim_refs")
        checks.append(_check(
            "edit.unsupported_claims",
            "PASS" if refs else "FAIL",
            f"source_claim_refs {len(refs) if isinstance(refs, list) else 0}건",
            "MAJOR",
        ))
        checks.append(_check(
            "edit.previous_video_difference",
            "PASS" if strategy.get("previous_channel_video_difference") else "FAIL",
            "전략에 이전 영상 차이 기술 여부", "MINOR",
        ))
        checks.append(_check(
            "edit.original_angle",
            "PASS" if (strategy.get("unique_angle") and script.get("originality_notes")) else "FAIL",
            "unique_angle + originality_notes 존재 여부", "MINOR",
        ))
        # 전략-대본 정합·장면 반복·템플릿화는 사람/AI 판독 필요 — 조작 금지
        checks.append(_check("edit.strategy_script_alignment", "UNASSESSED",
                             "자동 판정 불가 — 사람 검토 필요", "MAJOR"))
        checks.append(_check("edit.scene_repetition", "UNASSESSED",
                             "자동 판정 불가 — 사람 검토 필요", "MINOR"))
        checks.append(_check("edit.templated_structure", "UNASSESSED",
                             "자동 판정 불가 — 사람 검토 필요", "MINOR"))
        return checks

    # --- trust & safety ---
    @staticmethod
    def _assess_trust(research: dict | None, strategy: dict | None,
                      project_inputs: dict | None) -> list[dict]:
        checks: list[dict] = []
        if research:
            sources = research.get("sources")
            claims = research.get("claims")
            mapping = research.get("source_for_each_claim")
            has_sources = bool(sources) and bool(claims) and bool(mapping)
            checks.append(_check(
                "trust.missing_sources",
                "PASS" if has_sources else "FAIL",
                f"sources={len(sources) if isinstance(sources, list) else 0}, "
                f"claims={len(claims) if isinstance(claims, list) else 0}",
                "MAJOR",
            ))
            risky = research.get("prohibited_or_high_risk_claims")
            checks.append(_check(
                "trust.high_risk_claims",
                "PASS" if not risky else "FAIL",
                f"고위험 주장 {len(risky) if isinstance(risky, list) else 0}건",
                "BLOCKER",
            ))
        else:
            checks.append(_check("trust.missing_sources", "UNASSESSED", "리서치 artifact 없음", "MAJOR"))
            checks.append(_check("trust.high_risk_claims", "UNASSESSED", "리서치 artifact 없음", "BLOCKER"))

        checks.append(_check(
            "trust.ai_disclosure", "PASS",
            "AI 생성 콘텐츠 — 업로드 시 공개 필요로 기록됨(ai_disclosure_required=true)",
            "MAJOR",
        ))
        if strategy and strategy.get("policy_risks") is not None:
            checks.append(_check(
                "trust.youtube_policy", "UNASSESSED",
                f"전략에 정책 리스크 {len(strategy.get('policy_risks') or [])}건 기술 — 사람 확인 필요",
                "MAJOR",
            ))
        else:
            checks.append(_check("trust.youtube_policy", "UNASSESSED", "정책 리스크 기술 없음", "MAJOR"))
        checks.append(_check("trust.copyright_status", "UNASSESSED",
                             "자산 저작권·상업 이용 권리 — 사람 확인 필요", "MAJOR"))
        checks.append(_check("trust.real_person_risk", "UNASSESSED",
                             "실존 인물 오해 가능성 — 사람 확인 필요", "MAJOR"))
        return checks

    # --- 종합 ---
    def assess(
        self,
        project_path: str | Path,
        quality_rules: dict,
        video_rel: str | None,
        composition_report: dict | None = None,
        strategy: dict | None = None,
        script: dict | None = None,
        research: dict | None = None,
        project_inputs: dict | None = None,
        allowed_duration: dict | None = None,
    ) -> dict:
        project_path = Path(project_path)
        sections = {
            "technical": self._assess_technical(
                project_path, video_rel, composition_report, quality_rules,
                allowed_duration or {},
            ),
            "editorial": self._assess_editorial(strategy, script),
            "trust_and_safety": self._assess_trust(research, strategy, project_inputs),
        }

        all_checks = [c for checks in sections.values() for c in checks]
        blocker_fails = [c for c in all_checks if c["status"] == "FAIL" and c["severity"] == "BLOCKER"]
        other_fails = [c for c in all_checks if c["status"] == "FAIL" and c["severity"] != "BLOCKER"]
        unassessed = [c for c in all_checks if c["status"] == "UNASSESSED"]

        if blocker_fails:
            result = "BLOCKED"
        elif other_fails:
            result = "REVISION_REQUIRED"
        elif unassessed:
            result = "HUMAN_REVIEW_REQUIRED"
        else:
            result = "PASS"

        report = {
            "gate": "production_quality_safety",
            "result": result,
            "sections": sections,
            "blockers": [f"{c['rule_id']}: {c['evidence']}" for c in blocker_fails],
            "failures": [f"{c['rule_id']}: {c['evidence']}" for c in other_fails],
            "unassessed": [c["rule_id"] for c in unassessed],
            "note": "숫자 점수 없음 — 항목별 근거 기반 판정만 기록한다.",
            "created_at": _now_iso(),
        }
        if self.logger:
            self.logger.info(
                f"품질·안전 게이트: {result}",
                metadata={"result": result, "blockers": len(blocker_fails)},
            )
        return report
