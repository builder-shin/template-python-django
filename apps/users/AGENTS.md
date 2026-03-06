<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-06 | Updated: 2026-03-06 -->

# users

## Purpose
사용자(User) 도메인. Django AbstractUser를 확장하여 nickname, bio, avatar_url, status(ACTIVE/SUSPENDED/WITHDRAWN)를 제공. `/me` 엔드포인트로 현재 사용자 조회.

## Key Files

| File | Description |
|------|-------------|
| `models.py` | **User** 모델 — AbstractUser 확장. email(unique), nickname(2~50자), bio, avatar_url, Status(ACTIVE/SUSPENDED/WITHDRAWN). `save()`에서 nickname strip |
| `views.py` | **UsersViewSet** — ApiViewSet. ordering=["-date_joined"]. `me` 커스텀 액션(GET /api/v1/users/me). IsOwnerUser 권한 (자기 프로필만 수정) |
| `serializers.py` | **UserSerializer** — HookableSerializerMixin |
| `filters.py` | **UserFilter** — FilterSet |
| `urls.py` | `make_urlpatterns()` — basename="user" |
| `apps.py` | UsersConfig |

## For AI Agents

### Working In This Directory
- `AUTH_USER_MODEL = "users.User"` — 프로젝트 전체에서 이 모델 사용
- CoC 자동 추론: serializer_class, filterset_class 명시 불필요
- 권한: list/retrieve=AllowAny, me=IsAuthenticated, update/delete=IsAuthenticated+IsOwnerUser
- `/me` 엔드포인트: `@action(detail=False)` — request.user 반환

<!-- MANUAL: -->
