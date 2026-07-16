# -*- coding: utf-8 -*-
"""경쟁 채널 스캐너 — yt-dlp flat-playlist 출력을 분석해 주제 신호를 뽑는다.

핵심 신호: 채널 최근 N편의 중앙값 조회수 대비 배수(multiple_vs_median) ≥ 2.0
→ HIGH. 바이럴 1편이 평균을 왜곡하므로 중앙값이 기본이고 평균 배수는 병기한다.
근거: docs/superpowers/specs/2026-07-17-multilang-competitor-seo-triggers-design.md #2

순수 함수만 둔다 — 네트워크·subprocess 없음 (yt-dlp 실행은 scripts/scan_competitors.py).
"""
from statistics import median

SIGNAL_THRESHOLD = 2.0


def parse_flat_playlist(raw: dict) -> dict:
    """yt-dlp `-J --flat-playlist` 출력을 정규화한다.

    view_count가 없는 항목(멤버십·예정·비공개)은 건너뛰고 skipped_count에 센다.
    """
    entries = raw.get("entries") or []
    videos = []
    skipped = 0
    for entry in entries:
        if not entry or entry.get("view_count") is None:
            skipped += 1
            continue
        video_id = entry.get("id", "")
        videos.append(
            {
                "video_id": video_id,
                "title": entry.get("title", ""),
                "url": entry.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                "view_count": int(entry["view_count"]),
                "duration_seconds": entry.get("duration"),
                "upload_date": entry.get("upload_date"),
            }
        )
    return {
        "channel_name": raw.get("channel") or raw.get("uploader") or raw.get("title") or "",
        "channel_url": raw.get("channel_url") or raw.get("webpage_url") or "",
        "videos": videos,
        "skipped_count": skipped,
    }


def analyze_channel(parsed: dict, recent_n: int = 25) -> dict:
    """최근 N편 기준 평균/중앙값과 영상별 배수·신호를 계산한다."""
    recent = parsed["videos"][:recent_n]
    views = [video["view_count"] for video in recent]
    avg = (sum(views) / len(views)) if views else 0.0
    med = float(median(views)) if views else 0.0
    analyzed = []
    for video in recent:
        multiple_avg = round(video["view_count"] / avg, 2) if avg else 0.0
        multiple_med = round(video["view_count"] / med, 2) if med else 0.0
        analyzed.append(
            {
                **video,
                "multiple_vs_avg": multiple_avg,
                "multiple_vs_median": multiple_med,
                "signal": "HIGH" if multiple_med >= SIGNAL_THRESHOLD else "NORMAL",
            }
        )
    return {
        "channel_name": parsed["channel_name"],
        "channel_url": parsed["channel_url"],
        "video_count_scanned": len(recent),
        "skipped_count": parsed.get("skipped_count", 0),
        "avg_views": round(avg, 1),
        "median_views": med,
        "videos": analyzed,
    }


CSV_COLUMNS = [
    "channel", "title", "url", "view_count",
    "multiple_vs_median", "multiple_vs_avg", "signal",
    "upload_date", "duration_seconds",
]


def build_report(analyses: list[dict]) -> dict:
    """채널별 요약(전 영상 포함) + 전 채널 HIGH 신호 랭킹(중앙값 배수 내림차순)."""
    signals = [
        {**video, "channel_name": analysis["channel_name"]}
        for analysis in analyses
        for video in analysis["videos"]
        if video["signal"] == "HIGH"
    ]
    signals.sort(key=lambda video: video["multiple_vs_median"], reverse=True)
    return {
        "channel_count": len(analyses),
        "channels": [
            {
                "channel_name": analysis["channel_name"],
                "channel_url": analysis["channel_url"],
                "video_count_scanned": analysis["video_count_scanned"],
                "skipped_count": analysis["skipped_count"],
                "avg_views": analysis["avg_views"],
                "median_views": analysis["median_views"],
                "high_signal_count": sum(
                    1 for video in analysis["videos"] if video["signal"] == "HIGH"
                ),
                "videos": analysis["videos"],
            }
            for analysis in analyses
        ],
        "high_signals": signals,
    }


def report_to_csv_rows(report: dict) -> list[list]:
    """CSV 저장용 평탄화 — 헤더 + 전 채널 전 영상(중앙값 배수 내림차순)."""
    rows: list[list] = [list(CSV_COLUMNS)]
    pairs = [
        (channel["channel_name"], video)
        for channel in report["channels"]
        for video in channel["videos"]
    ]
    pairs.sort(key=lambda pair: pair[1]["multiple_vs_median"], reverse=True)
    for channel_name, video in pairs:
        rows.append([
            channel_name, video["title"], video["url"], video["view_count"],
            video["multiple_vs_median"], video["multiple_vs_avg"], video["signal"],
            video.get("upload_date") or "",
            video["duration_seconds"] if video.get("duration_seconds") is not None else "",
        ])
    return rows
