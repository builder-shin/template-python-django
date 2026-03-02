<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# comments

## Purpose
댓글(Comment) 도메인. Post에 대한 댓글 및 대댓글(self-referential parent) 구조를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `models.py` | **Comment** 모델 — post(FK→Post), content(1~2000자), parent(self FK, 대댓글), user_id. **CommentQuerySet** — by_post, by_user, recent, root_comments |
| `views.py` | **CommentsViewSet** — UserScopedMixin + ApiViewSet. allowed_includes=["post"], annotate(_reply_count) |
| `serializers.py` | **CommentSerializer** — HookableSerializerMixin. post(ResourceRelatedField), parent(ResourceRelatedField). computed: author_name, is_reply, reply_count |
| `filters.py` | **CommentFilter** — FilterSet |
| `urls.py` | DefaultRouter — basename="comment" |
| `apps.py` | CommentsConfig |

## For AI Agents

### Working In This Directory
- CoC 자동 추론: serializer_class, filterset_class 명시 불필요
- 대댓글: parent FK (self-referential), 같은 post의 댓글만 parent 가능 (clean() 검증)
- `allowed_includes = ["post"]` → PostSerializer 자동 추론
- reply_count: annotated `_reply_count` 우선 사용 (N+1 방지)
- related_name: Post → comments, Comment → replies

<!-- MANUAL: -->
