<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-06 -->

# posts

## Purpose
게시글(Post) 도메인. DRAFT → PUBLISHED → ARCHIVED 상태 워크플로우, user당 unique title, upsert(external_id 기반), 댓글 관계를 지원한다.

## Key Files

| File | Description |
|------|-------------|
| `models.py` | **Post** 모델 — Status(DRAFT/PUBLISHED/ARCHIVED), title(unique per user, Lower), content, view_count, external_id. `pre_save()`에서 title strip, published_at 자동 설정. `clean()`에서 발행 상태 검증 |
| `views.py` | **PostsViewSet** — ApiViewSet. `allowed_includes=["user", "comments"]`. 인증된 사용자만 자기 글 조회(`get_index_scope`). upsert(external_id 기반). `create_after_init`에서 user 자동 할당 |
| `serializers.py` | **PostSerializer** — HookableSerializerMixin. user/comments는 ResourceRelatedField(read_only). 미저장 인스턴스에서 comments 필드 제거 |
| `filters.py` | **PostFilter** — FilterSet |
| `urls.py` | `make_urlpatterns()` — basename="post" |
| `apps.py` | PostsConfig |

## For AI Agents

### Working In This Directory
- CoC 자동 추론: serializer_class, filterset_class 명시 불필요
- `allowed_includes = ["user", "comments"]` → included_serializers + queryset 최적화 자동 추론
- upsert: external_id 기반 (`PUT /api/v1/posts/upsert`)
- title: user당 unique (UniqueConstraint + Lower)
- 권한: list/retrieve=AllowAny, create=IsAuthenticated, update/delete=IsAuthenticated+IsOwnerOrReadOnly

### Model Lifecycle
```
pre_save() → title.strip(), published_at 자동 설정 (PUBLISHED 상태 신규)
clean() → 발행 상태 검증 (미래 published_at 불가, content 필수)
```

<!-- MANUAL: -->
