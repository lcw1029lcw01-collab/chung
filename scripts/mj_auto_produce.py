# -*- coding: utf-8 -*-
"""미드저니 자동 제작 브리지 — 이미지 생성 + 영상화(Animate Manually)까지.

동물심리 automation 툴킷(mj_batch_gen/mj_animate_batch_manual)을 ADOS
워크스페이스 단위로 이식했다. 미드저니는 API가 없으므로 디버그 크롬
(CDP :9222)을 Playwright로 제어한다 — 사전에 디버그 크롬에서 미드저니에
로그인되어 있어야 한다.

원 툴킷에서 확인된 함정을 그대로 반영:
- 제출 성공을 믿지 않는다 — 피드 adopt(프롬프트 매칭)로만 매핑 확정
- adopt 매칭 구분자: 프롬프트에 ", cinematic photoreal" 마커 필수
- /api/submit-jobs 응답은 success[] 배열만 파싱 (failure에도 job_id 있음)
- 이미지는 무손실 PNG(cdn .../{uuid}/0_{k}.png), 영상은 .../video/{uuid}/0.mp4
- relax 큐 지연: 청크 타임아웃 내 미완성이어도 재실행하면 adopt로 잡힘

입력: {workspace}/notes/mj/mj_shots.json
  {"shots": [{"id": "S01", "cut": 1, "prompt": "...(마커·플래그 포함 전체)",
              "motion": "...", "pick": 0}]}
상태: notes/mj/jobs.json (컷→이미지 uuid), notes/mj/videos.json
출력: {workspace}/images/{id}.png, {workspace}/motion/{id}.mp4

실행: 프로젝트 루트에서
  python scripts/mj_auto_produce.py {workspace} [images|collect|animate|videos|all]
"""
import base64
import io
import json
import re
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from playwright.sync_api import TimeoutError as PWTimeout  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

CORE_MARKER = ", cinematic photoreal"
INPUT_SEL = 'textarea[placeholder*="imagine" i]'
FETCH_B64 = (
    "async(u)=>{try{const r=await fetch(u);if(!r.ok)return r.status;const b=await r.blob();"
    "return await new Promise(res=>{const fr=new FileReader();fr.onload=()=>res(fr.result.split(',')[1]);"
    "fr.readAsDataURL(b);});}catch(e){return String(e);}}"
)

USAGE = """사용법: python scripts/mj_auto_produce.py {workspace} [phase]

  workspace: notes/mj/mj_shots.json 이 있는 수동 자산 워크스페이스
  phase    : images  — 이미지 생성 제출 + adopt 매핑
             collect — 매핑된 이미지 HD PNG 저장 → images/{id}.png
             animate — Animate Manually 제출 (모션 프롬프트)
             videos  — 렌더된 영상 저장 → motion/{id}.mp4
             all     — 위 4단계 순차 실행 (기본)

사전 조건: 디버그 크롬 실행 + 미드저니 로그인 + midjourney.com 탭."""


def jload(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


def jsave(path, obj):
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


class MJBridge:
    def __init__(self, workspace: Path, cdp: int = 9222):
        self.ws = workspace
        self.mj_dir = workspace / "notes" / "mj"
        order = jload(self.mj_dir / "mj_shots.json", None)
        if not order:
            sys.exit(f"작업 지시가 없습니다: {self.mj_dir / 'mj_shots.json'}")
        self.shots = order["shots"]
        self.by_cut = {int(shot["cut"]): shot for shot in self.shots}
        self.jobs = jload(self.mj_dir / "jobs.json", {})
        self.videos = jload(self.mj_dir / "videos.json", {})
        (workspace / "images").mkdir(exist_ok=True)
        (workspace / "motion").mkdir(exist_ok=True)

        self.pw = sync_playwright().start()
        browser = self.pw.chromium.connect_over_cdp(f"http://localhost:{cdp}")
        pages = [p for p in browser.contexts[0].pages if "midjourney" in p.url]
        if not pages:
            sys.exit("디버그 크롬에 midjourney.com 탭이 없습니다 — 1_크롬켜기 후 로그인하세요.")
        self.pg = pages[0]
        self.pg.bring_to_front()
        self.feed_url = None

    # --- 피드 / adopt ---
    def capture_feed(self):
        with self.pg.expect_response(
            lambda r: "/api/imagine?" in r.url and r.status == 200, timeout=30000
        ) as ri:
            self.pg.goto("https://www.midjourney.com/imagine", wait_until="domcontentloaded")
        self.feed_url = ri.value.url
        data = ri.value.json()
        return data.get("data", []) if isinstance(data, dict) else data

    def feed(self):
        try:
            data = self.pg.evaluate(
                "async(u)=>{const r=await fetch(u);return r.ok?await r.json():null;}", self.feed_url
            )
            if not data:
                return []
            return data.get("data", []) if isinstance(data, dict) else data
        except Exception:
            return []

    def feed_fresh(self):
        """피드를 페이지 리로드로 새로 캡처한다.

        시작 시점의 feed URL은 커서가 박혀 있어 이후 제출된 잡을 못 볼 수
        있다 — 원 툴킷에서 '재실행하면 adopt로 뒤늦게 잡히던' 원인.
        """
        try:
            return self.capture_feed()
        except Exception:
            return self.feed()

    @staticmethod
    def core_of(prompt: str) -> str:
        return prompt.split(CORE_MARKER)[0].strip()

    def adopt(self, feed_jobs):
        used = set(self.jobs.values())
        for job in feed_jobs:
            if job.get("event_type") != "diffusion":
                continue
            full_command = job.get("full_command") or ""
            uuid = job.get("id")
            if not uuid or uuid in used:
                continue
            for cut, shot in self.by_cut.items():
                if str(cut) in self.jobs:
                    continue
                core = self.core_of(shot["prompt"])
                if core and core in full_command:
                    self.jobs[str(cut)] = uuid
                    used.add(uuid)
                    break
        jsave(self.mj_dir / "jobs.json", self.jobs)

    def submit_prompt(self, prompt: str) -> bool:
        box = self.pg.locator(INPUT_SEL).first
        if not box.count():
            return False
        try:
            box.click()
            self.pg.keyboard.press("Control+A")
            self.pg.keyboard.press("Delete")
            box.fill(prompt)
            time.sleep(0.2)
            self.pg.keyboard.press("Enter")
            return True
        except Exception:
            return False

    # --- 1) 이미지 생성 ---
    def phase_images(self, batch: int = 3, timeout: int = 420):
        self.adopt(self.capture_feed())
        for _pass in range(1, 5):
            todo = [cut for cut in self.by_cut if str(cut) not in self.jobs]
            if not todo:
                break
            print(f"=== 이미지 패스 {_pass}: 남은 {len(todo)}컷 ===", flush=True)
            for i in range(0, len(todo), batch):
                chunk = todo[i : i + batch]
                submitted = []
                for cut in chunk:
                    if self.submit_prompt(self.by_cut[cut]["prompt"]):
                        submitted.append(cut)
                        print(f"  제출 #{cut} ({self.by_cut[cut]['id']})", flush=True)
                    time.sleep(2.5)
                deadline = time.time() + timeout
                while time.time() < deadline:
                    time.sleep(20)
                    self.adopt(self.feed_fresh())
                    if all(str(cut) in self.jobs for cut in submitted):
                        break
                done = [cut for cut in submitted if str(cut) in self.jobs]
                print(f"  청크 완료 {len(done)}/{len(submitted)} | 누적 {len(self.jobs)}/{len(self.by_cut)}", flush=True)
        left = [cut for cut in self.by_cut if str(cut) not in self.jobs]
        print(f"[이미지] 매핑 {len(self.jobs)}/{len(self.by_cut)} | 미완 {left}", flush=True)

    # --- 2) 이미지 수집 (HD PNG, pick 인덱스) — 렌더 완료까지 폴링 ---
    def phase_collect(self, timeout: int = 1200, poll: int = 30):
        deadline = time.time() + timeout
        while time.time() < deadline:
            pending = 0
            for cut, shot in self.by_cut.items():
                uuid = self.jobs.get(str(cut))
                dest = self.ws / "images" / f"{shot['id']}.png"
                if dest.is_file():
                    continue
                if not uuid:
                    pending += 1
                    continue
                pick = int(shot.get("pick", 0))
                result = self.pg.evaluate(
                    FETCH_B64, f"https://cdn.midjourney.com/{uuid}/0_{pick}.png"
                )
                if isinstance(result, str) and len(result) > 10000:
                    dest.write_bytes(base64.b64decode(result))
                    print(f"  {shot['id']}: {dest.stat().st_size // 1024}KB 저장", flush=True)
                else:
                    pending += 1
            if pending == 0:
                break
            print(f"  ...렌더 대기 {pending}컷", flush=True)
            time.sleep(poll)
        saved = sum(
            1 for shot in self.shots if (self.ws / "images" / f"{shot['id']}.png").is_file()
        )
        print(f"[수집] {saved}/{len(self.shots)}장 저장", flush=True)

    # --- 3) 영상화 제출 (Animate Manually) ---
    def animate_one(self, cut: int):
        shot = self.by_cut[cut]
        uuid = self.jobs.get(str(cut))
        if not uuid:
            print(f"  #{cut} 이미지 uuid 없음 — 스킵", flush=True)
            return None
        pick = int(shot.get("pick", 0))
        self.pg.goto(
            f"https://www.midjourney.com/jobs/{uuid}?index={pick}", wait_until="domcontentloaded"
        )
        for _ in range(30):
            if self.pg.locator('img[src*="cdn.midjourney"]').count() > 0:
                break
            time.sleep(2)
        time.sleep(1.5)
        try:
            btn = self.pg.get_by_role("button", name="Animate Manually").first
            btn.wait_for(state="visible", timeout=15000)
            btn.click()
        except Exception as exc:
            print(f"  #{cut} Animate Manually 버튼 실패: {exc}", flush=True)
            return "RETRY"
        time.sleep(2.5)
        try:
            box = self.pg.locator(INPUT_SEL).first
            box.wait_for(state="visible", timeout=10000)
            box.click()
            box.fill(shot.get("motion", "subtle gentle motion"))
        except Exception as exc:
            print(f"  #{cut} 모션 입력 실패: {exc}", flush=True)
            return "RETRY"
        try:
            low = self.pg.get_by_role("button", name="Low", exact=True)
            if low.count() > 0:
                low.first.click()
        except Exception:
            pass
        body = None
        try:
            with self.pg.expect_response(
                lambda r: r.request.method == "POST" and "/api/submit-jobs" in r.url, timeout=25000
            ) as ri:
                box.click()
                self.pg.keyboard.press("Enter")
            body = ri.value.json()
        except PWTimeout:
            return "RETRY"
        # 함정: failure[]에도 job_id가 있다 — success[]만 파싱
        success_ids = [
            item.get("job_id") for item in (body.get("success") or []) if item.get("job_id")
        ] if body else []
        if success_ids:
            self.videos.setdefault(str(cut), {})["uuid"] = success_ids[0]
            jsave(self.mj_dir / "videos.json", self.videos)
            print(f"  #{cut} 영상 제출 OK → {success_ids[0][:8]}", flush=True)
            return success_ids[0]
        failures = (body or {}).get("failure") or []
        messages = " ".join(f.get("message", "") for f in failures)
        if any(k in messages.lower() for k in ("queue", "too many", "limit", "concurrent")):
            print(f"  #{cut} 큐 참 — 대기 후 재시도", flush=True)
            return "QUEUE"
        print(f"  #{cut} 제출 실패: {messages[:80]}", flush=True)
        return None

    def phase_animate(self, gap: float = 4.0, queue_wait: float = 60.0):
        cuts = [
            cut for cut in self.by_cut
            if self.by_cut[cut].get("motion")
            and not self.videos.get(str(cut), {}).get("uuid")
            and not self.videos.get(str(cut), {}).get("file")
        ]
        print(f"[영상화 제출] 대상 {len(cuts)}컷", flush=True)
        i = 0
        while i < len(cuts):
            result = self.animate_one(cuts[i])
            if result == "QUEUE":
                time.sleep(queue_wait)
                continue
            if result == "RETRY":
                time.sleep(4)
                self.animate_one(cuts[i])
            i += 1
            time.sleep(gap)

    # --- 4) 영상 다운로드 ---
    def phase_videos(self, dl_timeout: int = 2400, poll: int = 25):
        pending = [
            cut for cut in self.by_cut
            if self.videos.get(str(cut), {}).get("uuid")
            and not self.videos.get(str(cut), {}).get("file")
        ]
        print(f"[영상 다운로드] 대기 {len(pending)}컷", flush=True)
        deadline = time.time() + dl_timeout
        while pending and time.time() < deadline:
            still = []
            for cut in pending:
                uuid = self.videos[str(cut)]["uuid"]
                shot = self.by_cut[cut]
                result = self.pg.evaluate(FETCH_B64, f"https://cdn.midjourney.com/video/{uuid}/0.mp4")
                if isinstance(result, str) and len(result) > 500:
                    dest = self.ws / "motion" / f"{shot['id']}.mp4"
                    dest.write_bytes(base64.b64decode(result))
                    self.videos[str(cut)]["file"] = dest.name
                    jsave(self.mj_dir / "videos.json", self.videos)
                    print(f"  {shot['id']}: {dest.stat().st_size // 1024}KB 저장", flush=True)
                else:
                    still.append(cut)
            pending = still
            if pending:
                time.sleep(poll)
        done = sum(1 for cut in self.by_cut if self.videos.get(str(cut), {}).get("file"))
        print(f"[영상] 저장 {done}/{len(self.by_cut)} | 미완 {pending}", flush=True)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(USAGE)
        return 1
    workspace = Path(argv[0])
    phase = argv[1] if len(argv) > 1 else "all"
    bridge = MJBridge(workspace)
    if phase in ("images", "all"):
        bridge.phase_images()
    if phase in ("collect", "all"):
        bridge.phase_collect()
    if phase in ("animate", "all"):
        bridge.phase_animate()
    if phase in ("videos", "all"):
        bridge.phase_videos()
    return 0


if __name__ == "__main__":
    sys.exit(main())
