<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-06 | Updated: 2026-03-14 -->

# auth

## Purpose
JWT 인증 시스템. 토큰 생성/검증, Redis 기반 토큰 스토어, login/refresh/logout API 뷰를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `jwt_utils.py` | `generate_token_pair(user)` — access+refresh 토큰 쌍 생성. `decode_token(token, expected_type)` — 서명+만료+타입+Redis jti 검증. `refresh_access_token()` — 리프레시 토큰 로테이션 (atomic revoke) |
| `token_store.py` | **TokenStore** — Redis(Django cache) 기반 토큰 저장소. `jti:{jti}` 키로 토큰 유효성 관리, `user_tokens:{user_id}`로 사용자별 토큰 목록 관리. `revoke_if_valid()` (atomic check-and-delete), `revoke_all_user_tokens()` (delete_many) 지원. Lazy prune (10개 초과 시 batch check) |
| `views.py` | **LoginView** (email+password→토큰쌍, AuthRateThrottle 10/min), **RefreshView** (토큰 로테이션), **LogoutView** (access+refresh 무효화, body에 refresh 포함 시 함께 revoke), **LogoutAllView** (사용자 전체 세션 무효화) |
| `serializers.py` | **LoginSerializer** (email+password), **RefreshSerializer** (refresh), **TokenResponseSerializer** (Swagger 문서용) |
| `urls.py` | `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/logout`, `/api/v1/auth/logout-all` |

## For AI Agents

### Working In This Directory
- JWT 설정: `settings.JWT_AUTH` (ACCESS 15분, REFRESH 7일, HS256)
- 토큰 검증 흐름: 서명 → 만료 → 타입(access/refresh) → Redis jti 존재 확인
- 리프레시 로테이션: revoke_if_valid로 replay attack 방지 (atomic check-and-delete)
- LoginView에 AuthRateThrottle 적용 (10/min per IP)
- LogoutView: body에 `refresh` 토큰 포함 시 access+refresh 모두 revoke (best-effort)
- 렌더러/파서: JSONRenderer/JSONParser (JSON:API 형식이 아닌 일반 JSON)

### Token Flow
```
Login → generate_token_pair() → Redis에 access_jti + refresh_jti 저장
  → 클라이언트에 {access, refresh} 반환

Request → Authorization: Bearer <access_token>
  → JWTAuthentication.authenticate() → decode_token(access)
  → Redis jti 확인 → User 조회 → (user, payload) 반환

Refresh → decode_token(refresh) → revoke_if_valid(old_refresh_jti)
  → generate_token_pair(user) → 새 토큰 쌍 발급

Logout → revoke_token(access_jti) + optionally revoke_token(refresh_jti)
LogoutAll → revoke_all_user_tokens(user_id) → 전체 jti 일괄 삭제
```

<!-- MANUAL: -->
