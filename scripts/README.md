# scripts/

운영 보조 스크립트 폴더.

빌드/검증/배포 등 ADOS 운영에 필요한 유틸리티 스크립트가 위치한다.
엔진 로직은 여기에 두지 않는다 (엔진은 engines/).

## Walking Skeleton 데모

모두 프로젝트 루트에서 실행한다.

```bash
# 샘플 채널 생성 (channels/future/) — 이미 있으면 안내만 출력
python scripts/create_sample_channel.py

# 샘플 프로젝트 생성 — 채널이 없으면 위 스크립트를 먼저 실행하라고 안내
python scripts/create_sample_project.py

# 전체 데모: 템플릿 로드 → 채널 준비 → 프로젝트 생성 → 요약 출력
python scripts/run_walking_skeleton_demo.py
```

사용 템플릿: `templates/future_documentary_template/template.yaml`
