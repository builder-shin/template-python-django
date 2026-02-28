<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# comments

## Purpose
댓글 도메인 API. 게시글에 대한 댓글 CRUD 및 대댓글(self-referential FK) 기능을 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `apps.py` | Django 앱 설정 (`CommentsConfig`) |
| `models.py` | `Comment` 모델 — Post FK, self-referential `parent` FK, `CommentQuerySet` |
| `serializers.py` | `CommentSerializer` — JSON:API 직렬화, `ResourceRelatedField`로 관계 해결 |
| `views.py` | `CommentsViewSet` — CRUD, `?include=post` 지원, 소유자 권한 검사 |
| `filters.py` | `CommentFilter` — Ransack 스타일 필터셋 |
| `urls.py` | URL 라우팅 (`/comments`, trailing_slash=False) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `migrations/` | Django DB 마이그레이션 |

## For AI Agents

### Working In This Directory
- `parent` FK는 self-referential (대댓글 지원) — null이면 루트 댓글
- 유효성 검증: 대댓글의 parent는 같은 post에 속해야 함
- `?include=post`로 댓글과 함께 게시글 sideload 가능
- `user_id`는 create 시 자동 설정 (인증된 유저)

### API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | `/api/v1/comments` | 댓글 목록 |
| POST | `/api/v1/comments` | 댓글 생성 |
| GET | `/api/v1/comments/:id` | 댓글 조회 |
| PATCH | `/api/v1/comments/:id` | 댓글 수정 (본인만) |
| DELETE | `/api/v1/comments/:id` | 댓글 삭제 (본인만) |

## Dependencies

### Internal
- `apps.posts` — Post 모델 ForeignKey
- `apps.core` — ApiViewSet, CrudActionsMixin, permissions, filters

<!-- MANUAL: -->
