<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# posts

## Purpose
게시글(Post) 도메인. DRAFT → PUBLISHED → ARCHIVED 상태 워크플로우, 조회수 추적, upsert(external_id 기반), 댓글 관계를 지원한다.

## Key Files

| File | Description |
|------|-------------|
| `models.py` | **Post** 모델 — Status(DRAFT/PUBLISHED/ARCHIVED), title(unique per user), content, view_count, external_id. **PostQuerySet** — recent, published_only, draft, archived, by_user, popular, statistics 등 |
| `views.py` | **PostsViewSet** — UserScopedMixin + ApiViewSet. allowed_includes=["comments"], annotate(_comment_count), upsert(external_id), publish 커스텀 액션 |
| `serializers.py` | **PostSerializer** — HookableSerializerMixin. computed fields: days_since_published, summary, author_name, is_publishable, comment_count |
| `filters.py` | **PostFilter** — FilterSet |
| `urls.py` | DefaultRouter — basename="post" |
| `apps.py` | PostsConfig |

## For AI Agents

### Working In This Directory
- CoC 자동 추론: serializer_class, filterset_class 명시 불필요
- `allowed_includes = ["comments"]` → included_serializers 자동 추론 (CommentSerializer)
- UserScopedMixin: create 시 user_id 자동 할당, update/destroy 시 소유권 체크
- upsert: external_id 기반 (`PUT /api/v1/posts/upsert`)
- publish: 커스텀 액션 (`POST /api/v1/posts/{id}/publish`)
- title: user당 unique (UniqueConstraint + Lower)
- comment_count: annotated `_comment_count` 우선 사용 (N+1 방지)

### Model Lifecycle
```
DRAFT → publish() → PUBLISHED (published_at 자동 설정)
any → archive() → ARCHIVED
```

<!-- MANUAL: -->
