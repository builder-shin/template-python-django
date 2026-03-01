<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# posts

## Purpose
게시글 도메인. 초안/게시/보관 상태 관리, 조회수, 외부 ID를 통한 upsert, 댓글 연관 관계 제공.

## Key Files

| File | Description |
|------|-------------|
| `models.py` | `Post` 모델 — Status(draft/published/archived), title/content/view_count/external_id + 풍부한 `PostQuerySet` |
| `views.py` | `PostsViewSet` — CRUD + `publish` 액션 + upsert (external_id 기반) + `?include=comments` |
| `serializers.py` | `PostSerializer` — days_since_published, summary, status_label(한국어), is_publishable, comment_count |
| `filters.py` | `PostFilter` — django-filter FilterSet (title, status, created_at, updated_at, user_id) |
| `urls.py` | `/api/v1/posts` 라우팅 (trailing_slash=False) |

## For AI Agents

### Working In This Directory
- Status: 0=draft(초안), 1=published(게시됨), 2=archived(보관됨)
- `get_index_scope()`: 인증된 사용자의 게시글만 반환 (`by_user`)
- `publish` 커스텀 액션: draft → published 전환 (content 필수)
- `upsert`: external_id 기반 find-or-create (JSON:API 파서 우회하여 raw body 파싱)
- `allowed_includes = ["comments"]` — `?include=comments` 지원
- UniqueConstraint: 같은 user_id 내 title 중복 불가 (case-insensitive)
- `published_at`: published 상태 전환 시 자동 설정
- `increment_view_count()`: F() expression으로 race condition 방지

### Testing Requirements
- `tests/posts/test_models.py` — 모델 생성, publish/archive, 유효성
- `tests/posts/test_api.py` — API CRUD, publish 액션, upsert, include

## Dependencies

### Internal
- `apps.comments` — `comments` 역참조 관계 (ForeignKey)
- `apps.core.views.ApiViewSet` — CRUD 라이프사이클 훅 내장 ViewSet
- `apps.core.mixins` — HookableSerializerMixin + OwnedResourceMixin

<!-- MANUAL: -->
