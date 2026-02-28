<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# auth_service

## Purpose
외부 인증 서비스(Rails 기반)와 연동하는 클라이언트 모듈. 세션 쿠키를 검증하고 사용자 정보를 가져오며, Circuit Breaker 및 Redis 캐싱을 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `apps.py` | Django 앱 설정 (`AuthServiceConfig`) |
| `client.py` | `AuthServiceClient` — 인증 서비스 HTTP 클라이언트, `CircuitBreaker`, 연결 풀링 |
| `current.py` | `Current` 클래스 re-export (`apps.core.middleware.current_user.Current`) |
| `models.py` | `AuthUser` dataclass — DB 비연동 사용자 모델 (외부 인증 서비스 응답 매핑) |

## For AI Agents

### Working In This Directory
- `AuthUser`는 DB 모델이 아님 — `@dataclass`로 정의, migrations 불필요
- `AuthServiceClient`는 모듈-레벨 싱글톤 패턴 사용 (`_circuit_breaker`, `_http_client`)
- 인증 서비스 URL: `settings.AUTH_SERVICE_URL` (기본 `http://localhost:3001`)
- 세션 캐시 TTL: `settings.AUTH_SESSION_CACHE_TTL` (기본 300초)

### Key Behaviors
- **Circuit Breaker**: 5회 실패 시 open, 30초 후 half-open 전환
- **재시도**: 502/503/504 응답 및 타임아웃 시 최대 2회 재시도
- **캐싱**: SHA256 해시된 토큰 키로 Redis 캐시 (TTL 300초)
- **연결 풀링**: httpx.Client 모듈 레벨 공유 (스레드 안전)

### Testing Requirements
- `AuthServiceClient` 테스트 시 httpx 응답 및 캐시를 mock
- Circuit Breaker 상태 테스트는 `AuthServiceClient.reset_circuit()` 호출 후 진행

## Dependencies

### External
- `httpx` — HTTP 클라이언트
- Django cache (Redis) — 세션 캐싱

<!-- MANUAL: -->
