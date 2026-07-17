# -*- coding: utf-8 -*-
"""경쟁 채널 스캔 — yt-dlp로 채널별 최근 영상을 전수 추출해 신호를 뽑는다.

API 키 불필요. 채널당 `yt-dlp -I 1:{N} -J {url}/videos` 1회 실행 — 조회수·업로드일 포함 전체 메타.
출력: report.json(채널 요약 + HIGH 신호 랭킹) + report.csv + raw_{슬러그}.json.

실행: 프로젝트 루트에서
  python scripts/scan_competitors.py {channel_url} [{channel_url} ...] [--channel {id}] [--recent-n 25]
  URL 없이 --channel만 주면 channels/{id}/competitors.yaml의 competitors 목록을 쓴다.
"""
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import load_yaml, write_json  # noqa: E402
from engines.research.competitor_scanner import (  # noqa: E402
    analyze_channel,
    build_report,
    parse_flat_playlist,
    report_to_csv_rows,
)

USAGE = """사용법: python scripts/scan_competitors.py {channel_url} [...] [--channel {id}] [--recent-n 25]

  channel_url : 유튜브 채널 URL (여러 개 가능)
  --channel   : 채널 id — 출력 위치(channels/{id}/research/)와
                URL 미지정 시 channels/{id}/competitors.yaml 목록 사용
  --recent-n  : 채널당 분석할 최근 영상 수 (기본 25)"""


def slugify(name: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z가-힣]+", "-", name).strip("-").lower()
    return slug or "channel"


def videos_url(url: str) -> str:
    url = url.rstrip("/")
    return url if url.endswith("/videos") else url + "/videos"


def run_yt_dlp(url: str, recent_n: int) -> dict:
    cmd = [
        "yt-dlp", "-I", f"1:{recent_n}", "-J",
        videos_url(url),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    # yt-dlp는 범위 내 일부 영상 실패(멤버십·삭제 등) 시에도 전체 JSON을
    # stdout에 내고 exit!=0으로 끝난다. stdout이 파싱되면 그걸 쓰고,
    # 정말 비었거나 깨졌을 때만 실패로 본다.
    stdout = (result.stdout or "").strip()
    if stdout:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            pass
    raise RuntimeError((result.stderr or "yt-dlp 실패").strip()[-500:])


def parse_args(argv: list[str]) -> dict | None:
    urls = []
    channel_id = None
    recent_n = 25
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--channel":
            if i + 1 >= len(argv):
                return None
            channel_id = argv[i + 1]
            i += 1
        elif arg == "--recent-n":
            if i + 1 >= len(argv):
                return None
            try:
                recent_n = int(argv[i + 1])
            except ValueError:
                return None
            if recent_n < 1:
                return None
            i += 1
        else:
            urls.append(arg)
        i += 1
    if not urls and channel_id:
        config_path = PROJECT_ROOT / "channels" / channel_id / "competitors.yaml"
        if config_path.is_file():
            config = load_yaml(config_path) or {}
            urls = [c["url"] for c in (config.get("competitors") or []) if c.get("url")]
    if not urls:
        return None
    return {"urls": urls, "channel_id": channel_id, "recent_n": recent_n}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args is None:
        print(USAGE)
        return 1

    date_tag = datetime.now(timezone.utc).strftime("%Y%m%d")
    if args["channel_id"]:
        out_dir = PROJECT_ROOT / "channels" / args["channel_id"] / "research" / f"competitor_scan_{date_tag}"
    else:
        out_dir = Path.cwd() / f"competitor_scan_{date_tag}"
    out_dir.mkdir(parents=True, exist_ok=True)

    analyses = []
    failed = []
    used_slugs = set()
    for url in args["urls"]:
        print(f"⏳ 추출 중 (최근 {args['recent_n']}편, 채널당 1~2분): {url}")
        try:
            raw = run_yt_dlp(url, args["recent_n"])
            parsed = parse_flat_playlist(raw)
            if not parsed["videos"]:
                print(f"⚠️ 영상 메타를 얻지 못함, 건너뜀: {url} (yt-dlp 업데이트 필요할 수 있음: pip install -U yt-dlp)")
                failed.append({"url": url, "error": "no_videos_extracted"})
                continue
            slug = slugify(parsed["channel_name"])
            if slug in used_slugs:
                suffix = 2
                while f"{slug}-{suffix}" in used_slugs:
                    suffix += 1
                slug = f"{slug}-{suffix}"
            used_slugs.add(slug)
            write_json(out_dir / f"raw_{slug}.json", raw)
            analyses.append(analyze_channel(parsed, recent_n=args["recent_n"]))
            print(f"✅ {parsed['channel_name']}: {len(parsed['videos'])}편 추출")
        except FileNotFoundError:
            print("yt-dlp가 설치되어 있지 않습니다. 설치: pip install yt-dlp")
            return 1
        except Exception as exc:
            print(f"⚠️ 추출 실패, 건너뜀: {url}\n   {exc}")
            failed.append({"url": url, "error": str(exc)})
            continue

    if not analyses:
        print("분석할 채널이 없습니다.")
        return 1

    report = build_report(analyses)
    report["failed_channels"] = failed
    report["recent_n"] = args["recent_n"]
    report["created_at"] = datetime.now(timezone.utc).isoformat()
    write_json(out_dir / "report.json", report)
    with (out_dir / "report.csv").open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(report_to_csv_rows(report))

    print(f"\n리포트 저장: {out_dir}")
    print(f"HIGH 신호 {len(report['high_signals'])}개 (중앙값 대비 ≥2.0배):")
    for signal in report["high_signals"][:10]:
        print(f"  {signal['multiple_vs_median']:>5.1f}x  [{signal['channel_name']}] {signal['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
