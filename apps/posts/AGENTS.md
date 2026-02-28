<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# posts

## Purpose
게시글 도메인 API. CRUD + 발행(publish)/보관(archive) 워크플로우, 조회수 추적, 댓글 연동을 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `apps.py` | Django 앱 설정 (`PostsConfig`) |
| `models.py` | `Post` 모델 — 상태(draft/published/archived), `PostQuerySet` 커스텀 매니저 |
| `serializers.py` | `PostSerializer` — JSON:API 직렬화, computed fields, links |
| `views.py` | `PostsViewSet` — CRUD + `publish` 커스텀 액션, 소유자 권한 검사 |
| `filters.py` | `PostFilter` — Ransack 스타일 필터셋 (title, status, created_at, user_id) |
| `urls.py` | URL 라우팅 (`/posts`, trailing_slash=False) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `migrations/` | Django DB 마이그레이션 |

## For AI Agents

### Working In This Directory
- Post는 3가지 상태: `DRAFT(0)`, `PUBLISHED(1)`, `ARCHIVED(2)` (IntegerChoices)
- `user_id`는 CharField — 외부 인증 서비스 ID 참조 (FK 아님)
- `external_id`는 unique nullable — upsert용 외부 시스템 연동 키
- `save()` 시 자동으로 `full_clean()` 호출 (update_fields 없을 때)
- UniqueConstraint: 같은 user의 title 중복 불가 (case-insensitive)

### API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | `/api/v1/posts` | 본인 게시글 목록 (get_index_scope 제한) |
| POST | `/api/v1/posts` | 게시글 생성 (user_id 자동 설정) |
| GET | `/api/v1/posts/:id` | 게시글 조회 |
| PATCH | `/api/v1/posts/:id` | 게시글 수정 (본인만) |
| DELETE | `/api/v1/posts/:id` | 게시글 삭제 (본인만) |
| POST | `/api/v1/posts/:id/publish` | 게시글 발행 (본인만) |
| GET | `/api/v1/posts/new` | 빈 게시글 템플릿 |
| PUT | `/api/v1/posts/upsert` | external_id 기반 upsert |

### Testing Requirements
- 모델 테스트: 상태 전환, 유효성 검증, QuerySet 메서드
- API 테스트: CRUD + publish + upsert, 권한 검사, JSON:API 형식

## Dependencies

### Internal
- `apps.core` — ApiViewSet, CrudActionsMixin, permissions, filters
- `apps.comments` — `comments` 역참조 (ForeignKey)

<!-- MANUAL: -->
