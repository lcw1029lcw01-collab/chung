# scripts/

운영 보조 스크립트 폴더.

빌드/검증/배포 등 ADOS 운영에 필요한 유틸리티 스크립트가 위치한다.
엔진 로직은 여기에 두지 않는다 (엔진은 engines/).

모든 스크립트는 **프로젝트 루트에서 실행**한다.

## 공통 안내

- **어떤 스크립트도 실제 업로드나 실제 외부 Provider 호출을 하지 않는다**
  (Midjourney/Typecast/YouTube 호출 없음, 실제 이미지·영상·음성 생성 없음).
- 스크립트가 만드는 런타임 산출물(`channels/`, `projects/`)은 **gitignore 대상**이라
  커밋되지 않는다.
- 전체 파이프라인은 dummy 모드로 동작하며, 산출물에는 placeholder임이 명시된다.

## ⭐ Canonical 명령

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
