# BGM 라이브러리 — AI 음악(Suno/Udio 등) 넣는 곳

이 폴더에 배경음악 트랙을 넣으면 합성 시 자동으로 믹싱된다:
- 영상 전체에 깔리고
- **나레이션이 나오는 구간에서는 자동으로 음량이 내려간다 (덕킹)**
- 시작·끝은 자동 페이드

음원이 없으면 BGM 없이 합성된다. 넣는 순간부터 적용.

## 만들 것: 채널 메인 테마 1곡

다큐는 보통 **한 곡을 영상 전체에 깐다** (곡을 여러 개 바꾸지 않음).
채널 정체성이 되는 메인 테마 1곡을 만들어 `main_theme.mp3`로 저장한다.

### 공통 스펙 (필수)

- **보컬 없음** — 순수 연주곡/앰비언트 (나레이션과 겹치면 안 됨)
- **드럼·강한 비트 금지** — 다큐 언더스코어는 존재감 없이 받쳐주는 역할
- 길이 3분 이상 (영상보다 짧으면 자동 루프됨)
- mp3 또는 wav, 파일명 `main_theme.mp3`

### Civilization 2100 채널 메인 테마 프롬프트 (Suno/Udio)

```
cinematic ambient documentary score, deep ethereal synth pads with sparse
minimal piano notes, a sense of vast future and quiet wonder, slow evolving,
teal and warm emotional tone, no drums, no vocals, instrumental, background underscore
```

무드를 바꾸고 싶으면:
- 더 신비롭게: `mysterious, cold, floating pads, distant`
- 더 희망적으로: `warm, hopeful, gentle rising strings`
- 더 긴장감: `subtle low pulse, suspenseful drone`

## 트랙을 다르게 쓰고 싶으면

`config/bgm_library.yaml`의 `default_track`을 파일명에 맞게 고친다.
프로젝트마다 다른 곡을 쓰려면 합성 시 지정할 수 있다:
`python scripts/compose_final_video.py {ws} {build} ko --bgm 파일명.mp3`

## 저작권

- Suno/Udio 유료 플랜 = 상업적 사용 가능 (약관 확인)
- 유튜브 오디오 라이브러리 음원도 가능 (저작자 표기 필요 여부 확인)
- 출처를 `config/bgm_library.yaml`의 `track_notes`에 기록할 것
