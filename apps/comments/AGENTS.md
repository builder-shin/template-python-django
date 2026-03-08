<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-08 | Updated: 2026-03-08 -->

# comments

## Purpose
댓글 관리 앱. Comment 모델, post FK, user FK, self-referential parent FK (대댓글), nested reply 구조.

## Files

| File | Purpose |
|------|---------|
| `models.py` | Comment 모델 — post FK, content (validators: min 1, max 2000), user FK, parent self-FK (replies). Indexes: (post, created_at). Validation: parent must belong to same post. |
| `views.py` | CommentsViewSet (CoC pattern) — no explicit serializer_class/filterset_class. Permissions: AllowAny for list/retrieve, IsAuthenticated for create, IsOwnerOrReadOnly for update/delete. select_related_extra: ["user"]. allowed_includes: ["post"]. create_after_init sets user. |
| `serializers.py` | Serializer (HookableSerializerMixin). Auto-generated from models. |
| `filters.py` | FilterSet (django_filters). Auto-generated from models. |
| `urls.py` | URL routing via make_urlpatterns() — auto-generated. |
| `migrations/` | Django database migrations (see `migrations/AGENTS.md`). |

## For AI Agents

### Working In This Directory
- ViewSet inherits from `apps.core.views.ApiViewSet`
- Serializer inherits from `HookableSerializerMixin` as first parent
- CoC pattern: `serializer_class`, `filterset_class`, `queryset` are auto-inferred from app path and model name
- select_related_extra = ["user"] optimizes queries to fetch user in one DB call
- Comment.parent is optional (null/blank) for top-level comments
- Nested replies: child comments have parent pointing to top-level or another reply
- Validation enforces parent.post_id == comment.post_id (no cross-post replies)

### Model Lifecycle
- **Create**: user sets instance.user in create_after_init
- **Validation**: parent must belong to same post as comment
- **Deletion**: CASCADE from post (if post deleted, all comments deleted)
- **Deletion**: CASCADE from parent (if parent reply deleted, all child replies deleted)

### Permissions
- **list/retrieve**: AllowAny (public)
- **create**: IsAuthenticated
- **update/delete**: IsAuthenticated + IsOwnerOrReadOnly
- Comments inherit permission inheritance from Post (both AllowAny for read)

### Includes/Relationships
- allowed_includes: ["post"]
- Use `?include=post` to nest full post object
- Parent-child relationships exposed via parent FK (replies access via parent serializer)

<!-- MANUAL: -->
