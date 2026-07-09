# engines/

ADOS의 엔진 구현이 위치하는 폴더.

`docs/09` ~ `docs/31`에 정의된 엔진들이 여기에 구현된다:
Channel, Brand, Portfolio, Project, Memory, Provider, Workflow Orchestrator,
Timeline, Research, Knowledge, Story, Direction, Visual, Motion, Voice,
Subtitle, Editing, Quality, Growth, Publishing, Analytics, Learning, AI Evolution.

- 엔진은 Provider를 직접 호출하지 않는다 (반드시 Provider Adapter 경유).
- 각 엔진의 Implementation Classes 섹션이 구현 기준이다.
