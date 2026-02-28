<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# tests/auth_service

## Purpose
AuthServiceClient 단위 테스트. Circuit Breaker, 캐싱, 재시도 로직을 검증한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `test_client.py` | AuthServiceClient 테스트 — 세션 검증, 캐싱, Circuit Breaker, 에러 처리 |

## For AI Agents

### Working In This Directory
- httpx 응답을 mock하여 다양한 시나리오 테스트
- `AuthServiceClient.reset_circuit()`으로 테스트 간 Circuit Breaker 초기화
- Redis 캐시를 mock 또는 테스트 캐시 백엔드 사용

<!-- MANUAL: -->
