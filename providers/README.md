# providers/

외부/내부 Provider Adapter가 위치하는 폴더. (`docs/14_PROVIDER_ENGINE.md`)

현재 Provider:
- midjourney (Visual)
- midjourney_video (Motion)
- typecast (Voice)
- internal_subtitle (Subtitle)
- internal_editing (Editing)

Engine → Provider Interface → Adapter 순서로만 호출한다.
