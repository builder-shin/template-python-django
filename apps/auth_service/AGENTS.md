<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# auth_service

## Purpose
외부 인증 서비스 연동 클라이언트. session_web 쿠키로 인증하고 `AuthUser` dataclass를 반환. 서킷 브레이커, 캐싱, 재시도, 커넥션 풀링 내장.

## Key Files

| File | Description |
|------|-------------|
| `client.py` | `AuthServiceClient` — httpx 기반 인증 서비스 클라이언트 (CircuitBreaker, Redis 캐싱, 재시도 2회) |
| `models.py` | `AuthUser` dataclass — 비DB 사용자 모델 (id, email, name, workspace_id, workspace_kind, workspace_role, member_status) |
| `current.py` | `Current` re-export — `apps.core.middleware.current_user.Current` 바로가기 |
| `apps.py` | Django AppConfig |

## For AI Agents

### Working In This Directory
- `AuthUser`는 Django 모델이 아님 — DB 테이블 없음, dataclass 기반
- `AuthServiceClient.verify_session(token)` → `AuthUser | None`
- 서킷 브레이커: 5회 실패 → 30초 open → half_open (자동 복구)
- Redis 캐시: SHA256(token) 키, TTL 300초 (설정 가능)
- 재시도: 502/503/504 응답 또는 타임아웃 시 최대 2회, 0.1초 간격
- httpx.Client 싱글턴 — 커넥션 풀링 (프로세스 로컬, thread-safe)
- 인증 서비스 엔드포인트: `GET /api/auth/me` (session_web 쿠키 전달)

### Testing Requirements
- `tests/auth_service/test_client.py`에서 respx mock 사용
- `conftest.py`의 `mock_authenticated`, `mock_unauthenticated` fixture 활용
- 서킷 브레이커 테스트 시 `AuthServiceClient.reset_circuit()` 호출

### Common Patterns
- 예외 계층: `AuthenticationError` (401) → `ServiceUnavailableError` → `CircuitOpenError`
- 응답 파싱: `{ "success": true, "data": { "id": ..., ... } }` 형식

## Dependencies

### External
- httpx — HTTP 클라이언트 (커넥션 풀링)
- Django cache (Redis) — 세션 캐시

<!-- MANUAL: -->
