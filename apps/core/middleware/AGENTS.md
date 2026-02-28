<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# middleware

## Purpose
Django 미들웨어 모듈. 보안(IP 차단), 현재 사용자 스레드 로컬 관리, 구조화 로깅을 처리한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `allow2ban.py` | `Allow2BanMiddleware` — 의심스러운 요청 패턴 감지 후 자동 IP 차단 (Rails Rack::Attack 동등) |
| `current_user.py` | `CurrentUserMiddleware` + `Current` — 스레드 로컬에 현재 유저/request_id 저장 |
| `structured_logging.py` | `StructuredLoggingMiddleware` — JSON 형식 요청/응답 로깅, 민감 데이터 필터링 |

## For AI Agents

### Working In This Directory
- 미들웨어 순서 중요: `config/settings/base.py`의 `MIDDLEWARE` 리스트 참조
- `Allow2BanMiddleware`는 Redis 캐시 사용 — 테스트 시 캐시 mock 필요
- `Current` 클래스: `Current.get_user()`, `Current.get_request_id()` — 어디서든 현재 유저 접근
- `StructuredLoggingMiddleware`는 민감 필드(password, token, secret 등) 자동 필터링

### Key Behaviors
- **Allow2Ban**: 20회 의심 요청 시 1시간 자동 차단 (wp-admin, .env, phpinfo 등)
- **CurrentUser**: DRF 인증 후 thread-local에 유저 저장, 요청 완료 시 자동 정리
- **StructuredLogging**: method, path, status, duration_ms, remote_ip, user_id, request_id 포함

<!-- MANUAL: -->
