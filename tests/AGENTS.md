<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# tests

## Purpose
pytest 기반 테스트 스위트. apps/ 구조를 미러링하여 도메인별 테스트 디렉토리 구성. 팩토리, 공통 fixture, JSON:API 헬퍼 제공.

## Key Files

| File | Description |
|------|-------------|
| `conftest.py` | 공통 fixture — `auth_user` (Django User), `mock_authenticated`, `mock_unauthenticated`, `api_client`, `authenticated_client`, `jsonapi_headers`, `jsonapi_payload()` |
| `factories.py` | factory-boy 팩토리 — `MemberFactory`, `PostFactory`, `CommentFactory` (faker ko_KR 로케일) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `comments/` | 댓글 모델 + API 테스트 (see `comments/AGENTS.md`) |
| `core/` | CrudActionsMixin 테스트 (see `core/AGENTS.md`) |
| `members/` | 회원 모델 + API 테스트 (see `members/AGENTS.md`) |
| `posts/` | 게시글 모델 + API 테스트 (see `posts/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 인증 필요 테스트: `mock_authenticated` fixture + `client.force_authenticate(user=mock_authenticated)` 사용
- JSON:API 요청: `jsonapi_headers` + `jsonapi_payload(attributes, resource_type)` 사용
- 팩토리: faker ko_KR 로케일 — 한국어 이름/문장 생성
- 실행: `pytest` (루트) 또는 `make test`, 커버리지: `make test-cov`
- 설정: `config.settings.test` (LocMemCache, 스로틀링 비활성화, Celery eager)

### Testing Requirements
- 커버리지 최소 80% (`pyproject.toml` fail_under)
- 마커: `@pytest.mark.slow` (느린 테스트 표시)
- DB 테스트: `@pytest.mark.django_db` 필수

### Common Patterns
- API 테스트 패턴: `APIClient()` → `force_authenticate(user=mock_authenticated)` → 요청
- 모델 테스트 패턴: `Model.objects.create(...)` → assert
- 인증 시나리오: `mock_authenticated`(인증됨), `mock_unauthenticated`(미인증)

## Dependencies

### External
- pytest + pytest-django — 테스트 프레임워크
- factory-boy + faker — 테스트 데이터 생성
- freezegun — 시간 모킹

<!-- MANUAL: -->
