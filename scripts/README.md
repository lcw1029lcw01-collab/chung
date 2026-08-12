# scripts/

운영 보조 스크립트 폴더.

빌드/검증/배포 등 ADOS 운영에 필요한 유틸리티 스크립트가 위치한다.
엔진 로직은 여기에 두지 않는다 (엔진은 engines/).

모든 스크립트는 **프로젝트 루트에서 실행**한다.

## 공통 안내

- **대부분의 스크립트는 실제 업로드나 외부 Provider 호출을 하지 않는다.**
  단, 아래 두 스크립트는 **실제 외부 작업과 비용이 발생할 수 있다**:
  - `generate_narration.py` — **Typecast API를 실제로 호출**해 음성을 생성한다 (크레딧 소모).
  - `mj_auto_produce.py` — 디버그 크롬(CDP)으로 **미드저니에 실제 작업을 제출**한다
    (구독 사용량 소모).
  이 둘을 제외한 스크립트는 Midjourney/Typecast/YouTube를 호출하지 않는다.
  어떤 스크립트도 YouTube 업로드는 하지 않는다.
- 스크립트가 만드는 런타임 산출물(`channels/`, `projects/`)은 **gitignore 대상**이라
  커밋되지 않는다.
- dummy 파이프라인의 산출물에는 placeholder임이 명시된다.
  production 파이프라인(`ados.py`)은 placeholder 산출물을 통과시키지 않는다.

## ⭐ Canonical 명령

### Production (실제 제작 워크플로우 — `ados.py`)

```bash
# 환경 점검 (필수 의존성 누락 시 non-zero exit)
python scripts/check_environment.py

# 템플릿 번들 검증
python scripts/ados.py template validate future_documentary_template

# production 프로젝트 생성 (채널의 템플릿 번들 snapshot + workflow 초기화)
python scripts/ados.py project create --channel civilization_2100 --topic "주제" --duration 900

# 게이트/입력 대기까지 실행 → 상태/다음 행동 확인
python scripts/ados.py project run-until-gate PROJECT_PATH
python scripts/ados.py project status PROJECT_PATH
python scripts/ados.py project next PROJECT_PATH

# creative 단계 결과 import (work order 스키마 검증 + placeholder 거부)
python scripts/ados.py project import-result PROJECT_PATH STAGE_ID RESULT_FILE

# 사람 승인 / 재시도
python scripts/ados.py project approve PROJECT_PATH STAGE_ID --decision APPROVE --reviewer human
python scripts/ados.py project retry PROJECT_PATH STAGE_ID [--force]
```

외부 호출이 선언된 stage는 config(`allow_external_calls`)와 `--allow-external`이
둘 다 있어야 실행된다. 이 CLI는 업로드를 수행하지 않는다.

### Dummy 데모 (레거시 walking skeleton)

```bash
# 전체 dummy 파이프라인 (샘플 채널/프로젝트 → 20단계 완주 → 실행 보고서)
python scripts/run_full_dummy_pipeline.py

# 업로드 준비 (전체 완주 + 자산/검토/최종게이트/메타패키지/운영보고 — upload_ready False가 정상)
python scripts/run_upload_preparation_demo.py
```

## 기본 샘플 생성

```bash
# 샘플 채널 생성 (channels/future/) — 이미 있으면 안내만 출력
python scripts/create_sample_channel.py

# 샘플 프로젝트 생성 — 채널이 없으면 위 스크립트를 먼저 실행하라고 안내
python scripts/create_sample_project.py
```

## Provider / 자산

```bash
# Provider placeholder 데모 — 외부 호출 없음(NOT_SUBMITTED) 확인
python scripts/run_provider_placeholder_demo.py

# 수동 자산 등록 데모 — placeholder 경로 메타데이터만 등록 (파일 복사 없음)
python scripts/run_manual_asset_registration_demo.py

# v0.2 Provider 통합 준비 데모 — 수동 작업용 export pack(MJ/MJ Video/Typecast) 생성,
# provider job 추적, 외부 생성 자산 메타데이터 import + AssetRegistry 연결까지.
# 여전히 외부 API를 호출하지 않으며, upload_ready는 false를 유지한다.
python scripts/run_provider_integration_prep_demo.py
```

## v0.2 수동 제작 루프

```bash
# 수동 제작 루프 데모 — 수동 워크스페이스(manual_assets/{project_id}/, gitignore 대상)와
# asset intake manifest를 만들고 최종 준비도를 재실행한다.
# 실물 파일 배치·검토 승인이 없으므로 upload_ready는 **false가 정상**이다.
python scripts/run_manual_production_loop_demo.py

# 수동 검토 데모 — 사람 검토 체크포인트 전체를 명시적으로 승인한다.
# **검토 승인만으로는 부족하다**: 실물 자산·최종 영상이 없으므로
# upload_ready는 여전히 false다.
python scripts/run_manual_review_demo.py

# ⚠️ TEST ONLY 업로드 게이트 시뮬레이션 — gitignore된 manual_assets/ 안에
# 아주 작은 **가짜 placeholder 파일**을 만들어 게이트 로직만 증명한다.
# 결과가 upload_ready true여도 실제 제작 준비 완료가 절대 아니며,
# placeholder를 실제 미디어로 취급하거나 업로드에 사용하면 안 된다.
python scripts/run_test_only_upload_gate_simulation.py
```

## v0.3 실제 수동 트라이얼

첫 실제 파일 기반 수동 제작 트라이얼 흐름. **어느 단계도 업로드하지 않는다.**

```bash
# 1) 준비 — 트라이얼 가이드(기대 파일명·배치 경로)·체크리스트·워크스페이스·
#    export pack을 생성한다. 이후 사람이 직접 파일을 만들어 배치해야 한다.
python scripts/run_real_manual_trial_prepare.py

# 2) 검증 — 사람이 배치한 파일을 존재/확장자/최소 크기로만 검사한다
#    (미디어 내용 검사 없음). 파일 미비·검토 미승인이면 upload_ready false.
python scripts/run_real_manual_trial_validate.py {project_path}

# 3) 최종화 — 게이트·수동 업로드 패키지를 재생성한다. 업로드는 수행하지 않으며,
#    사람이 manual_upload_instructions에 따라 직접 업로드한다.
python scripts/run_real_manual_trial_finalize.py {project_path}
```

validate/finalize는 project_path 인자가 없으면 사용법만 출력한다.

## AI Documentary Engine v1 (프리미엄 다큐 연출 계층)

```bash
# 다큐멘터리 연출 계층 데모 — 더미 파이프라인을 Direction까지 실행한 뒤
# 채널 다큐 바이블(카메라/컬러/캐릭터/모티프), 25분 자산 비율 계획,
# 씬→샷 분해 리스트, 샷별 MJ 프롬프트 블루프린트, 플래그십 에피소드
# 청사진(목표 95점)을 생성한다.
# 이 계층은 샷/프롬프트 **블루프린트**를 만들 뿐, 실제 미디어는 만들지 않는다.
# 근거: docs/35_AI_DOCUMENTARY_ENGINE_V1.md
python scripts/run_documentary_engine_v1_demo.py
```

## Scene Script / Director / World Bible / SEO 계층

```bash
# "영상은 글이 아니라 장면(Scene)으로 만든다" + "Prompt는 결과물, Director가 먼저" —
# 세계관 바이블(연속된 미래사) → 장면 대본(+GPT 작성 가이드) → 감독 연출 결정
# (감정→카메라/렌즈/색감/조명/음악) → 장면 기반 샷 리스트 → MJ/모션 프롬프트
# 블루프린트 → SEO 패키지(제목 20+20·챕터·태그)까지 생성한다.
# 이미지·영상 프로바이더는 미드저니 고정 (docs/38 #6).
# 실제 미디어 생성·업로드 없음. 근거: docs/37, docs/38
python scripts/run_scene_script_engine_demo.py
```

## ⚠️ 실제 외부 Provider 호출 스크립트 (비용 발생)

아래 두 스크립트는 **실제 외부 작업을 생성하며 비용/사용량이 발생한다.**
실행 전 무엇이 제출되는지 반드시 확인하라.

```bash
# Typecast 신형 API로 나레이션 wav 실제 생성 (크레딧 소모)
# 입력: {workspace}/narration_blocks.json + channels/{channel_id}/narration_profile.yaml
python scripts/generate_narration.py {workspace} {channel_id} [--voice tc_xxx] [--emotion normal]

# 미드저니 자동 제작 브리지 — 디버그 크롬(CDP :9222)으로 실제 이미지/영상 작업 제출
# 사전 조건: 디버그 크롬 실행 + 미드저니 로그인 (구독 사용량 소모)
python scripts/mj_auto_produce.py {workspace} [images|collect|animate|videos|all]
```

## 최종 영상 합성 (자막 번인 — 로컬 ffmpeg 실행)

```bash
# 수동 워크스페이스의 빌드 세그먼트를 재조립하고 자막을 번인한 뒤,
# 자막이 실제 프레임에 보이는지 검증한다 (docs/36).
# 외부 API 호출·업로드는 없다 — 로컬 ffmpeg만 사용한다.
python scripts/compose_final_video.py {workspace_dir} [build_subdir] [lang]
# 예) python scripts/compose_final_video.py manual_assets/20260710-141033-future-million-year-human notes/build3min ko
```

## 단계별 데모 (디버깅용)

아래 스크립트들은 파이프라인의 **특정 구간만 따로 돌려볼 때** 유용하다.
전체 실행은 canonical 명령(`run_full_dummy_pipeline.py`)을 사용한다.

```bash
# Template → Channel → Project 최소 흐름
python scripts/run_walking_skeleton_demo.py

# Workflow 초기화 + Timeline (TIMELINE 완료까지)
python scripts/run_workflow_timeline_demo.py

# RESEARCH → KNOWLEDGE → STORY (DIRECTION 도달)
python scripts/run_research_knowledge_story_demo.py

# DIRECTION → TIMELINE → VISUAL (MOTION 도달)
python scripts/run_direction_timeline_visual_demo.py

# MOTION → VOICE → SUBTITLE → EDITING (QUALITY 도달)
python scripts/run_motion_voice_subtitle_editing_demo.py

# QUALITY → AUTO_FIX(skip) → PACKAGE → READY → PUBLISHED → ANALYTICS → LEARNING (AI_EVOLUTION 도달)
python scripts/run_quality_publishing_analytics_learning_demo.py
```

사용 샘플 템플릿: `templates/future_documentary_template/template.yaml`
