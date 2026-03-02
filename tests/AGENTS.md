<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# tests

## Purpose
pytest 기반 테스트 스위트. 앱별 디렉토리로 구성되며, conftest.py에서 공통 fixture를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `conftest.py` | 공통 fixture — `auth_user`, `mock_authenticated`, `mock_unauthenticated`, `api_client`, `authenticated_client`, `jsonapi_headers`, `jsonapi_payload()` |
| `factories.py` | Factory Boy 팩토리 정의 — `MemberFactory`, `PostFactory`, `CommentFactory` (faker ko_KR 로케일) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `comments/` | Comment 모델/API 테스트 (see `comments/AGENTS.md`) |
| `core/` | Core 인프라 테스트 — CoC 추론, CrudActions (see `core/AGENTS.md`) |
| `members/` | Member 모델/API 테스트 (see `members/AGENTS.md`) |
| `posts/` | Post 모델/API 테스트 (see `posts/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 설정: `config.settings.test` (LocMemCache, 스로틀링 비활성화, Celery eager)
- 실행: `pytest` 또는 `make test`, 커버리지: `make test-cov`
- 모든 HTTP 호출 차단: respx.mock autouse fixture (WebMock 패턴)
- JSON:API 페이로드: `jsonapi_payload(attributes, resource_type)` 헬퍼 사용
- 인증 사용자: `mock_authenticated` fixture + `client.force_authenticate(user=mock_authenticated)`
- 미인증 테스트: `mock_unauthenticated` fixture
- 테스트 파일 명명: `test_models.py` (모델 단위), `test_api.py` (API 통합)

### Testing Requirements
- 커버리지 최소 80% (`pyproject.toml` fail_under)
- 마커: `@pytest.mark.slow` (느린 테스트 표시)
- DB 테스트: `@pytest.mark.django_db` 필수

### Common Patterns
```python
# API 테스트 패턴
def test_something(self, mock_authenticated, jsonapi_headers):
    client = APIClient()
    client.force_authenticate(user=mock_authenticated)
    response = client.get("/api/v1/resources", **jsonapi_headers)
    assert response.status_code == 200
```

## Dependencies

### External
- pytest + pytest-django — 테스트 프레임워크
- factory-boy + faker — 테스트 데이터 생성 (ko_KR 로케일)
- freezegun — 시간 모킹

<!-- MANUAL: -->
