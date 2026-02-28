<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# members

## Purpose
회원 프로필 도메인 API. 사용자 프로필 CRUD 및 상태(활성/정지/탈퇴) 관리를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `apps.py` | Django 앱 설정 (`MembersConfig`) |
| `models.py` | `Member` 모델 — 상태(active/suspended/withdrawn), `MemberQuerySet` |
| `serializers.py` | `MemberSerializer` — JSON:API 직렬화, 한국어 status_label |
| `views.py` | `MembersViewSet` — CRUD + `me` 커스텀 액션, 소유자 권한 검사 |
| `filters.py` | `MemberFilter` — Ransack 스타일 필터셋 |
| `urls.py` | URL 라우팅 (`/members`, trailing_slash=False) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `migrations/` | Django DB 마이그레이션 |

## For AI Agents

### Working In This Directory
- `user_id`는 unique CharField — 외부 인증 서비스 ID (한 유저당 한 프로필)
- Member 상태: `ACTIVE(0)`, `SUSPENDED(1)`, `WITHDRAWN(2)` (IntegerChoices)
- `get_index_scope()`는 전체 목록 반환 (posts와 다름 — 공개 프로필)
- nickname은 strip 처리, 2~50자

### API Endpoints
| Method | Path | Action |
|--------|------|--------|
| GET | `/api/v1/members` | 회원 목록 |
| POST | `/api/v1/members` | 프로필 생성 (user_id 자동 설정) |
| GET | `/api/v1/members/:id` | 프로필 조회 |
| PATCH | `/api/v1/members/:id` | 프로필 수정 (본인만) |
| DELETE | `/api/v1/members/:id` | 프로필 삭제 (본인만) |
| GET | `/api/v1/members/me` | 내 프로필 조회 |

## Dependencies

### Internal
- `apps.core` — ApiViewSet, CrudActionsMixin, permissions, filters

<!-- MANUAL: -->
