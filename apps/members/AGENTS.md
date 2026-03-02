<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# members

## Purpose
회원 프로필 도메인. 외부 인증 서비스의 user_id와 연결되는 프로필 정보(닉네임, 자기소개, 아바타) 관리.

## Key Files

| File | Description |
|------|-------------|
| `models.py` | `Member` 모델 — Status(active/suspended/withdrawn), nickname, bio, avatar_url + `MemberQuerySet` |
| `views.py` | `MembersViewSet` — CRUD + `/me` 커스텀 액션 (본인 프로필 조회) |
| `serializers.py` | `MemberSerializer` — display_name 포함 |
| `filters.py` | `MemberFilter` — django-filter FilterSet (nickname, status, user_id, created_at, updated_at) |
| `urls.py` | `/api/v1/members` 라우팅 (trailing_slash=False) |

## For AI Agents

### Working In This Directory
- `user_id`는 CharField (외부 인증 서비스 UUID) — Django auth.User와 무관
- Status: 0=active(활성), 1=suspended(정지), 2=withdrawn(탈퇴)
- `create_after_init`: user_id를 request.user.id에서 자동 설정
- `update_after_init`, `destroy_after_init`: 본인 확인 (user_id 비교)
- `me` 액션: user_id로 프로필 조회
- nickname은 save() 시 strip() 처리, full_clean() 자동 호출

### Testing Requirements
- `tests/members/test_models.py` — 모델 생성, 상태 변경, 유효성
- `tests/members/test_api.py` — API CRUD, 인증, 권한 테스트

## Dependencies

### Internal
- `apps.core.views.ApiViewSet` — CRUD 라이프사이클 훅 내장 ViewSet
- `apps.core.mixins` — HookableSerializerMixin
- `django_filters` — 표준 필터 프레임워크

<!-- MANUAL: -->
