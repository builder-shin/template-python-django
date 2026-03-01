<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# middleware

## Purpose
커스텀 Django 미들웨어 3종. IP 자동 차단, 현재 사용자 스레드 로컬, 구조화 로깅 제공.

## Key Files

| File | Description |
|------|-------------|
| `allow2ban.py` | `Allow2BanMiddleware` — 의심 경로 스캔 공격 IP 자동 차단 (Redis 캐시, 20회/60초 → 1시간 ban) |
| `current_user.py` | `CurrentUserMiddleware` + `Current` 클래스 — 스레드 로컬에 현재 사용자/request_id 저장 (Rails Current 패턴) |
| `structured_logging.py` | `StructuredLoggingMiddleware` — JSON 포맷 요청 로깅 (method, path, status, duration, user_id, params) |

## For AI Agents

### Working In This Directory
- 미들웨어 순서: Allow2Ban → (Django 기본) → CurrentUser → StructuredLogging
- `Current.get_user()` — DRF 인증 후에만 유효 (미들웨어 단계에서는 None)
- Allow2Ban 의심 패턴: `/etc/passwd`, `wp-admin`, `wp-login`, `.env`, `phpinfo`, `phpmyadmin`
- 민감 데이터 필터링: `FILTERED_PARAMS` (password, token, secret, api_key, credit_card, ssn)
- 클라이언트 IP: `HTTP_X_FORWARDED_FOR` 우선, fallback `REMOTE_ADDR`

### Testing Requirements
- Allow2Ban: Redis 캐시 의존 — 테스트 시 LocMemCache로 대체됨
- CurrentUser: 스레드 로컬 정리 확인 (finally 블록)

<!-- MANUAL: -->
