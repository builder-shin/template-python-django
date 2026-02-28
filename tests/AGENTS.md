<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# tests

## Purpose
pytest 기반 테스트 스위트. `apps/` 디렉토리 구조를 미러링하며, 모델 단위 테스트와 API 통합 테스트를 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `conftest.py` | pytest 공통 fixture (인증 유저, API 클라이언트 등) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `auth_service/` | AuthServiceClient 테스트 (see `auth_service/AGENTS.md`) |
| `comments/` | Comment 모델 및 API 테스트 (see `comments/AGENTS.md`) |
| `core/` | CrudActionsMixin 테스트 (see `core/AGENTS.md`) |
| `members/` | Member 모델 및 API 테스트 (see `members/AGENTS.md`) |
| `posts/` | Post 모델 및 API 테스트 (see `posts/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 테스트 실행: `pytest` (루트에서)
- settings: `config.settings.test`
- 테스트 파일 네이밍: `test_*.py`
- 새 앱 테스트 추가 시: `tests/{app_name}/` 디렉토리 생성 + `__init__.py` 추가
- JSON:API 형식으로 요청/응답 테스트 (`TEST_REQUEST_DEFAULT_FORMAT = "vnd.api+json"`)

### Testing Requirements
- 모델 테스트: `test_models.py` — 유효성 검증, 비즈니스 로직, QuerySet 메서드
- API 테스트: `test_api.py` — 엔드포인트 CRUD, 권한, 필터링
- `conftest.py`의 공통 fixture 활용

<!-- MANUAL: -->
