# prompts/

Provider에 보낼 프롬프트 **템플릿**이 놓일 폴더. (Midjourney visual / video motion,
Typecast voice script 등 Engine이 생성하는 프롬프트의 템플릿)

## 현재 비어 있다 — 의도된 상태다

production 경로에는 아직 LLM adapter가 연결되지 않았다. creative 단계는 프롬프트를
자동 생성하지 않고, work order를 만들어 사람이 결과를 작성해 import한다
(`engines/workflow/executors.py`의 `creative_workflow_executor`).
따라서 채울 템플릿이 아직 없다.

`engines/visual/visual_engine.py`와 `engines/direction/direction_engine.py`가 만드는
프롬프트는 워킹 스켈레톤용 더미다 — `"prompt_mode": "dummy"`, `production_ready: false`,
`DUMMY_DISCLAIMER`가 붙는다. 이걸 템플릿의 근거로 삼지 말 것.

LLM adapter가 붙는 시점에 이 폴더가 채워진다.

## creative 지시문을 여기로 옮기지 말 것

`engines/workflow/executors.py`의 `CREATIVE_SPECS`에 있는 `instructions`는
여기로 빼내지 않는다. 같은 dict의 키가 `build_default_registry()`에서
**executor allowlist**를 만들고, `instructions`는 그 단계의 `schema`·`output_rel`과
한 계약을 이룬다. 분리하면 allowlist 경계가 데이터로 새고 계약이 두 곳으로 갈라진다.
지시문을 고칠 일이 있으면 `executors.py`에서 고친다.
