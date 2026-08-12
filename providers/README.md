# providers/

외부/내부 Provider Adapter가 위치하는 폴더. (`docs/14_PROVIDER_ENGINE.md`)

현재 Provider:
- midjourney (Visual)
- midjourney_video (Motion)
- thumbnail (Thumbnail)
- typecast (Voice)
- internal_subtitle (Subtitle)
- internal_editing (Editing)

thumbnail은 이미지를 만들지 않는다. 채널 `brand_profile.yaml`의 `thumbnail_style`과
`research/content_strategy.json`의 `thumbnail_hypotheses`를 합쳐 수동 작업 팩을 만든다.
근거가 없으면 팩을 만들지 않고 `ADOSValidationError`를 낸다 — 썸네일 안을 지어내지 않는다.

Engine → Provider Interface → Adapter 순서로만 호출한다.
