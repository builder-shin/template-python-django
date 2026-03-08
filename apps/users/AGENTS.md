<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-08 | Updated: 2026-03-08 -->

# users

## Purpose
사용자 관리 앱. User 모델 (AbstractUser 확장), 상태 관리 (ACTIVE/SUSPENDED/WITHDRAWN), /me 엔드포인트.

## Files

| File | Purpose |
|------|---------|
| `models.py` | User model (extends AbstractUser) — email unique, nickname (validators: min 2, max 50), bio (TextField), avatar_url (URLField), status (ACTIVE/SUSPENDED/WITHDRAWN). Indexes: status. full_clean on save, strips nickname. |
| `views.py` | UsersViewSet (CoC pattern) — serializer_class CoC auto-inferred; filterset_class dynamically generated from allowed_filters dict. Permissions: AllowAny for list/retrieve, IsAuthenticated for me, IsOwnerUser for update/delete. ordering: -date_joined. /me action returns current authenticated user. |
| `serializers.py` | Serializer (HookableSerializerMixin). Auto-generated from models. |
| `urls.py` | URL routing via make_urlpatterns() — auto-generated. |
| `migrations/` | Django database migrations (see `migrations/AGENTS.md`). |

## For AI Agents

### Working In This Directory
- ViewSet inherits from `apps.core.views.ApiViewSet`
- Serializer inherits from `HookableSerializerMixin` as first parent
- CoC pattern: `serializer_class`, `queryset` are auto-inferred from app path and model name
- `filterset_class` is dynamically generated from the `allowed_filters` dict defined on the ViewSet
- User extends Django's AbstractUser (first_name, last_name, username, password inherited)
- Custom fields: email (unique), nickname, bio, avatar_url, status
- User.save() calls full_clean() unless update_fields specified, ensuring validation always runs
- User.nickname is stripped of whitespace on save

### Model Lifecycle
- **Create**: inherit AbstractUser behavior; full_clean validates all fields
- **Status**: ACTIVE (0), SUSPENDED (1), WITHDRAWN (2) for account lifecycle
- **Validation**: email unique (enforced by DB unique constraint); nickname required if provided (min 2 chars)
- **Display**: __str__ returns nickname if set, else username

### Permissions
- **list/retrieve**: AllowAny (public user profiles)
- **me**: IsAuthenticated (get current user)
- **update/delete**: IsAuthenticated + IsOwnerUser (users can only modify their own profile)
- IsOwnerUser permission: allows GET/HEAD/OPTIONS for all; write access only for own user ID

### Actions
- **list**: `GET /users/` — list all users (paginated)
- **retrieve**: `GET /users/{id}/` — get single user
- **me**: `GET /users/me/` — get current authenticated user (requires IsAuthenticated)
- **create**: `POST /users/` — register new user (handled by built-in create)
- **update**: `PATCH /users/{id}/` — update own profile only
- **partial_update**: `PATCH /users/{id}/` — partial update
- **destroy**: `DELETE /users/{id}/` — delete own account only

### Includes/Relationships
- No includes configured (User is leaf; other models FK to User)

<!-- MANUAL: -->
