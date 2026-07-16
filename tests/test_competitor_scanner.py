# -*- coding: utf-8 -*-
"""경쟁 채널 스캐너 테스트 — 픽스처 dict만 사용, 네트워크 없음.

실행: 프로젝트 루트에서  python -m unittest tests.test_competitor_scanner -v
"""
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engines.research.competitor_scanner import (  # noqa: E402
    CSV_COLUMNS,
    analyze_channel,
    build_report,
    parse_flat_playlist,
    report_to_csv_rows,
)

RAW = {
    "channel": "미래탐사단",
    "channel_url": "https://www.youtube.com/@future-lab",
    "entries": [
        {"id": "v1", "title": "영상 1", "url": "https://youtu.be/v1",
         "view_count": 1000, "duration": 600, "upload_date": "20260701"},
        {"id": "v2", "title": "영상 2", "view_count": 2000, "duration": 700},
        {"id": "v3", "title": "영상 3", "view_count": 3000, "duration": 800},
        {"id": "v4", "title": "떡상 영상", "view_count": 10000, "duration": 900},
        {"id": "v5", "title": "멤버십 영상", "view_count": None},
        None,
    ],
}


class TestParseFlatPlaylist(unittest.TestCase):
    def test_parse_and_skip(self):
        parsed = parse_flat_playlist(RAW)
        self.assertEqual(parsed["channel_name"], "미래탐사단")
        self.assertEqual(len(parsed["videos"]), 4)
        self.assertEqual(parsed["skipped_count"], 2)

    def test_url_fallback_from_id(self):
        parsed = parse_flat_playlist(RAW)
        self.assertEqual(parsed["videos"][1]["url"], "https://www.youtube.com/watch?v=v2")

    def test_empty_entries(self):
        parsed = parse_flat_playlist({"channel": "빈 채널", "entries": None})
        self.assertEqual(parsed["videos"], [])
        self.assertEqual(parsed["skipped_count"], 0)


class TestAnalyzeChannel(unittest.TestCase):
    def test_avg_median_and_multiples(self):
        analysis = analyze_channel(parse_flat_playlist(RAW))
        # views [1000, 2000, 3000, 10000] → avg 4000, median 2500
        self.assertEqual(analysis["avg_views"], 4000.0)
        self.assertEqual(analysis["median_views"], 2500.0)
        top = analysis["videos"][3]
        self.assertEqual(top["multiple_vs_median"], 4.0)
        self.assertEqual(top["multiple_vs_avg"], 2.5)
        self.assertEqual(top["signal"], "HIGH")
        self.assertEqual(analysis["videos"][0]["signal"], "NORMAL")

    def test_threshold_boundary_is_high(self):
        raw = {"channel": "경계", "entries": [
            {"id": "a", "view_count": 100}, {"id": "b", "view_count": 100},
            {"id": "c", "view_count": 200},
        ]}
        analysis = analyze_channel(parse_flat_playlist(raw))
        # median 100 → 200은 정확히 2.0배 → HIGH (경계 포함)
        self.assertEqual(analysis["videos"][2]["signal"], "HIGH")

    def test_recent_n_slices_from_front(self):
        analysis = analyze_channel(parse_flat_playlist(RAW), recent_n=2)
        self.assertEqual(analysis["video_count_scanned"], 2)
        self.assertEqual(analysis["avg_views"], 1500.0)

    def test_empty_channel_no_division_error(self):
        analysis = analyze_channel(parse_flat_playlist({"entries": []}))
        self.assertEqual(analysis["video_count_scanned"], 0)
        self.assertEqual(analysis["avg_views"], 0.0)


class TestBuildReport(unittest.TestCase):
    def analyses(self):
        second = {"channel": "채널B", "entries": [
            {"id": "b1", "view_count": 100}, {"id": "b2", "view_count": 100},
            {"id": "b3", "title": "B 떡상", "view_count": 500},
        ]}
        return [
            analyze_channel(parse_flat_playlist(RAW)),
            analyze_channel(parse_flat_playlist(second)),
        ]

    def test_high_signals_ranked_desc(self):
        report = build_report(self.analyses())
        self.assertEqual(report["channel_count"], 2)
        multiples = [s["multiple_vs_median"] for s in report["high_signals"]]
        self.assertEqual(multiples, sorted(multiples, reverse=True))
        self.assertEqual(report["high_signals"][0]["title"], "B 떡상")  # 5.0배
        self.assertEqual(report["high_signals"][0]["channel_name"], "채널B")

    def test_channel_summary_counts(self):
        report = build_report(self.analyses())
        first = report["channels"][0]
        self.assertEqual(first["high_signal_count"], 1)
        self.assertEqual(len(first["videos"]), 4)


class TestCsvRows(unittest.TestCase):
    def test_header_and_sorted_rows(self):
        report = build_report([analyze_channel(parse_flat_playlist(RAW))])
        rows = report_to_csv_rows(report)
        self.assertEqual(rows[0], CSV_COLUMNS)
        self.assertEqual(len(rows), 1 + 4)
        self.assertEqual(rows[1][1], "떡상 영상")  # 배수 내림차순 첫 행
        self.assertEqual(rows[1][6], "HIGH")

    def test_missing_optional_fields_blank(self):
        report = build_report([analyze_channel(parse_flat_playlist(RAW))])
        rows = report_to_csv_rows(report)
        # v2는 upload_date가 없다 → 빈 문자열
        v2_row = next(r for r in rows[1:] if r[1] == "영상 2")
        self.assertEqual(v2_row[7], "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
