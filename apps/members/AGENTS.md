<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# members

## Purpose
회원 프로필(Member) 도메인. Django auth.User와 별도로 프로필 정보를 관리하며, `/me` 엔드포인트로 현재 사용자 프로필을 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `models.py` | **Member** 모델 — user_id(unique), nickname(2~50자), bio, avatar_url, Status(ACTIVE/SUSPENDED/WITHDRAWN). **MemberQuerySet** — active, suspended, by_user, recent |
| `views.py` | **MembersViewSet** — UserScopedMixin + ApiViewSet. `me` 커스텀 액션 (`GET /api/v1/members/me`) |
| `serializers.py` | **MemberSerializer** — HookableSerializerMixin. computed: display_name |
| `filters.py` | **MemberFilter** — FilterSet |
| `urls.py` | DefaultRouter — basename="member" |
| `apps.py` | MembersConfig |

## For AI Agents

### Working In This Directory
- CoC 자동 추론: serializer_class, filterset_class 명시 불필요
- user_id: auth.User.id와 연결 (CharField, unique)
- `/me` 엔드포인트: 로그인 사용자의 프로필 반환
- nickname: strip() 자동 처리 (clean + save)

<!-- MANUAL: -->
