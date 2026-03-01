<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# comments

## Purpose
댓글 도메인. Post에 대한 댓글 및 대댓글(self-referential) 지원. Post와 N:1 관계.

## Key Files

| File | Description |
|------|-------------|
| `models.py` | `Comment` 모델 — post(FK), content, user_id, parent(self FK) + `CommentQuerySet` |
| `views.py` | `CommentsViewSet` — CRUD + `?include=post` 지원 |
| `serializers.py` | `CommentSerializer` — ResourceRelatedField(post, parent), author_name, is_reply, reply_count |
| `filters.py` | `CommentFilter` — django-filter FilterSet (content, user_id, post, parent, created_at, updated_at) |
| `urls.py` | `/api/v1/comments` 라우팅 (trailing_slash=False) |

## For AI Agents

### Working In This Directory
- `parent` FK로 대댓글 구현 — 같은 post 내에서만 허용 (`clean()` 검증)
- `allowed_includes = ["post"]` — `?include=post` 지원
- `included_serializers`: post → PostSerializer (JSON:API include 관계)
- `ResourceRelatedField`로 관계 필드 처리 — `is_valid()` 시 자동 resolve
- `create_after_init`: user_id 자동 설정
- `update/destroy_after_init`: 본인 댓글만 수정/삭제 가능

### Testing Requirements
- `tests/comments/test_models.py` — 모델 생성, 대댓글 유효성
- `tests/comments/test_api.py` — API CRUD, include, 권한

## Dependencies

### Internal
- `apps.posts.models.Post` — ForeignKey 관계
- `apps.posts.serializers.PostSerializer` — included_serializers
- `apps.core.views.ApiViewSet` — CRUD 라이프사이클 훅 내장 ViewSet
- `apps.core.mixins` — HookableSerializerMixin + OwnedResourceMixin

<!-- MANUAL: -->
