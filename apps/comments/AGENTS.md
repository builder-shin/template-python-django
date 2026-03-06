<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-06 -->

# comments

## Purpose
댓글(Comment) 도메인. Post에 대한 댓글 및 대댓글(self-referential parent) 구조를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `models.py` | **Comment** 모델 — post(FK→Post), content(1~2000자), user(FK→User), parent(self FK, 대댓글). `clean()`에서 대댓글이 같은 글인지 검증 |
| `views.py` | **CommentsViewSet** — ApiViewSet. `allowed_includes=["post"]`, `select_related_extra=["user"]`. `create_after_init`에서 user 자동 할당 |
| `serializers.py` | **CommentSerializer** — HookableSerializerMixin. post(ResourceRelatedField, writable), parent(optional), user(read_only). `validate_post`: 발행된 게시글만 댓글 가능 |
| `filters.py` | **CommentFilter** — FilterSet |
| `urls.py` | `make_urlpatterns()` — basename="comment" |
| `apps.py` | CommentsConfig |

## For AI Agents

### Working In This Directory
- CoC 자동 추론: serializer_class, filterset_class 명시 불필요
- 대댓글: parent FK (self-referential), 같은 post의 댓글만 parent 가능 (`clean()` 검증)
- `allowed_includes = ["post"]` → PostSerializer 자동 추론
- related_name: Post.comments, Comment.replies
- 권한: list/retrieve=AllowAny, create=IsAuthenticated, update/delete=IsAuthenticated+IsOwnerOrReadOnly

<!-- MANUAL: -->
