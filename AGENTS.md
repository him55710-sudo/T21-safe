# T21-safe 개발 규칙

## 브랜치 및 디렉터리 소유권

- `agent/research-data`: `docs/research`, `docs/regulatory`, `docs/safety`, `research`, `tools/datasets`
- `agent/signal-engine`: `services/api`, `services/engine`, `models`, `contracts`, `tests/backend`
- `agent/product-ui`: `apps/web`, `infra`, `tests/frontend`, 루트 `README.md`, `AGENTS.md`, `docker-compose.yml`

각 브랜치에서는 지정된 범위만 수정한다. 다른 브랜치의 소유 범위를 변경해야 하면 해당 브랜치 담당 작업으로 넘기고, 통합 시 명시적으로 검토한다.

## 안전 경계

- LLM 에이전트는 연구자료 정리와 개발 검토에만 사용한다.
- 실시간 환자 위험도 계산 경로에는 LLM을 포함하지 않는다.
- 실제 inference는 버전이 고정된 deterministic signal pipeline과 검증 가능한 통계·ML 모델만 사용한다.
- 모델, 데이터셋, 전처리 및 임계값 버전을 추적 가능하게 고정하고 검증 결과를 기록한다.
