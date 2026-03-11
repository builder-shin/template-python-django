<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-08 -->

# middleware

## Purpose
Django HTTP 미들웨어. 요청 처리 파이프라인에서 JWT 유저 추출 등의 횡단 관심사를 처리한다.

## Key Files

| File | Description |
|------|-------------|
| `jwt_user.py` | **JWTUserMiddleware** — JWT에서 user_id를 추출하여 경량 `_JWTUser` 객체를 `request.user`에 설정. DB 쿼리 없음. django-structlog 로깅용. 보안 경계가 아님 (DRF JWTAuthentication이 실제 인증 담당) |

## For AI Agents

### Working In This Directory
- 미들웨어 등록 순서 (base.py MIDDLEWARE):
  1. `CorsMiddleware`
  2. `SecurityMiddleware`
  3. `CSPMiddleware`
  4. `CommonMiddleware`
  5. `JWTUserMiddleware` ← 로깅용 유저 설정
  6. `RequestMiddleware` (structlog)

<!-- MANUAL: -->
