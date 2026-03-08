<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-08 | Updated: 2026-03-08 -->

# posts

## Purpose
게시글 관리 앱. Post 모델, 발행/아카이브/초안 상태 워크플로우, external_id 기반 upsert 기능, 비공개/공개 제어.

## Files

| File | Purpose |
|------|---------|
| `models.py` | Post 모델 — title, content, view_count, status (DRAFT/PUBLISHED/ARCHIVED), published_at, user FK, external_id unique. Indexes: status. Constraints: unique title per user (case-insensitive). pre_save: strips title, sets published_at on first publish. |
| `views.py` | PostsViewSet (CoC pattern) — serializer_class CoC auto-inferred; filterset_class dynamically generated from allowed_filters dict. Permissions: AllowAny for list/retrieve, IsAuthenticated for create, IsOwnerOrReadOnly for update/delete. get_index_scope filters by current user. allowed_includes: user, comments. upsert by external_id. create_after_init sets user. |
| `serializers.py` | Serializer (HookableSerializerMixin). Auto-generated from models. |
| `urls.py` | URL routing via make_urlpatterns() — auto-generated. |
| `migrations/` | Django database migrations (see `migrations/AGENTS.md`). |

## For AI Agents

### Working In This Directory
- ViewSet inherits from `apps.core.views.ApiViewSet`
- Serializer inherits from `HookableSerializerMixin` as first parent
- CoC pattern: `serializer_class`, `queryset` are auto-inferred from app path and model name
- `filterset_class` is dynamically generated from the `allowed_filters` dict defined on the ViewSet
- Post.pre_save() is called on save (via BaseModel)
- Post status choices: DRAFT (0), PUBLISHED (1), ARCHIVED (2)
- published_at is set automatically on first PUBLISHED transition
- external_id field enables upsert workflows (null/blank allowed)
- Unique constraint on (Lower(title), user) ensures no duplicate titles per user

### Model Lifecycle
- **Create**: user sets instance.user in create_after_init; pre_save strips title
- **Publish**: on transition to PUBLISHED, published_at is set to now() (only if not already set)
- **Update**: upsert by external_id supported (see upsert_after_init, upsert_find_params)
- **Validation**: published_at cannot be in future; PUBLISHED posts require content

### Permissions
- **list/retrieve**: AllowAny (public)
- **create**: IsAuthenticated
- **update/delete**: IsAuthenticated + IsOwnerOrReadOnly
- get_index_scope: authenticated users see own posts only; unauthenticated users see none (filtered in list)

### Includes/Relationships
- allowed_includes: ["user", "comments"]
- Use `?include=user` to nest user object
- Use `?include=comments` to nest related comments

<!-- MANUAL: -->
