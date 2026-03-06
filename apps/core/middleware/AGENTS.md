<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-06 -->

# middleware

## Purpose
Django HTTP 미들웨어. 요청 처리 파이프라인에서 IP 차단, JWT 유저 추출 등의 횡단 관심사를 처리한다.

## Key Files

| File | Description |
|------|-------------|
| `allow2ban.py` | **Allow2BanMiddleware** — 정적 IP 차단(settings.BLOCKED_IPS) + 동적 자동 차단(의심 패턴 20회/60초 → 1시간 ban). Redis 기반 카운터. 의심 패턴: wp-admin, .env, phpinfo 등 |
| `jwt_user.py` | **JWTUserMiddleware** — JWT에서 user_id를 추출하여 경량 `_JWTUser` 객체를 `request.user`에 설정. DB 쿼리 없음. django-structlog 로깅용. 보안 경계가 아님 (DRF JWTAuthentication이 실제 인증 담당) |

## For AI Agents

### Working In This Directory
- 미들웨어 등록 순서 (base.py MIDDLEWARE):
  1. `CorsMiddleware`
  2. `SecurityMiddleware`
  3. `CSPMiddleware`
  4. `Allow2BanMiddleware` ← IP 차단
  5. `CommonMiddleware`
  6. `JWTUserMiddleware` ← 로깅용 유저 설정
  7. `RequestMiddleware` (structlog)
- IP 추출: `apps.core.utils.get_client_ip` (django-ipware 기반) 사용

<!-- MANUAL: -->
