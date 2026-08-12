# employees/

AI Employee 정의가 위치할 폴더. (`docs/04_AI_ORGANIZATION.md` §38 Suggested Code Mapping —
`base/`, `departments/`, `managers/` 구조를 제안한다)

ADOS에서는 "Agent"라는 단어를 쓰지 않는다. AI Employee를 사용한다.

## 현재 비어 있다

`docs/04`의 CEO(사용자) → COO → Portfolio/Channel/Project Manager → Department 구조는
아직 파이썬 클래스로 구현되지 않았다.

지금 실제로 돌아가는 역할 정의는 **`templates/<template>/roles.yaml`**이다.
README가 말하는 "역할·책임·KPI·입력/출력·실패 조건"이 거기에
`role_id` · `responsibility` · `kpi` · `required_inputs` · `expected_outputs` ·
`failure_conditions`로 들어가 있고, `allowed_step_kinds` · `can_approve` ·
`can_trigger_external_action`으로 권한까지 제한한다.

역할을 고칠 일이 있으면 지금은 `roles.yaml`을 고친다.
이 폴더를 채우게 되면 그때 `roles.yaml`과의 관계를 먼저 정리할 것 —
두 곳에 같은 역할이 따로 살면 안 된다.
