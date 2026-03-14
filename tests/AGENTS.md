<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-14 -->

# tests

## Purpose
pytest 기반 테스트 스위트. 앱별 디렉토리로 구성되며, conftest.py에서 공통 fixture를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `conftest.py` | 공통 fixture — `auth_user`, `mock_authenticated`, `api_client`, `authenticated_client`, `jsonapi_headers`, `jsonapi_payload()`, `auth_tokens`, `access_token`, `jwt_authenticated_client`. `block_outbound_http` autouse fixture (respx) |
| `factories.py` | Factory Boy 팩토리 정의 |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `core/` | Core 인프라 테스트 — CoC 추론, CrudActions, auth, health (see `core/AGENTS.md`) |
| `users/` | User 모델/API 테스트 (see `users/AGENTS.md`) |
| `posts/` | Post 모델/API 테스트 (see `posts/AGENTS.md`) |
| `comments/` | Comment 모델/API 테스트 (see `comments/AGENTS.md`) |
| `snapshots/` | API 스키마 스냅샷 (`api_schema.json`) — `make update-schema`로 갱신, `test_schema_snapshot.py`에서 비교 |

## For AI Agents

### Working In This Directory
- 설정: `config.settings.test`
- 실행: `make test` (권장), 커버리지: `make test-cov`. 반드시 `uv run`으로 실행하라 (`uv run pytest`).
- CI 커버리지 최소: 80% (`--cov-fail-under=80`)
- 모든 HTTP 호출 차단: `respx.mock` autouse fixture
- JSON:API 페이로드: `jsonapi_payload(attributes, resource_type)` 헬퍼 사용
- 인증 테스트: `mock_authenticated` + `force_authenticate()` 또는 `jwt_authenticated_client` (JWT Bearer)
- 테스트 파일 명명: `test_models.py` (모델 단위), `test_api.py` (API 통합)
- DB 테스트: `@pytest.mark.django_db` 필수

### Common Patterns
```python
# API 테스트 패턴 (force_authenticate)
def test_something(self, mock_authenticated, jsonapi_headers):
    client = APIClient()
    client.force_authenticate(user=mock_authenticated)
    response = client.get("/api/v1/resources", **jsonapi_headers)
    assert response.status_code == 200

# JWT 인증 테스트 패턴
def test_with_jwt(self, jwt_authenticated_client, jsonapi_headers):
    response = jwt_authenticated_client.get("/api/v1/resources", **jsonapi_headers)
    assert response.status_code == 200
```

<!-- MANUAL: -->
