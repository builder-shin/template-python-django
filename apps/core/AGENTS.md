<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# core

## Purpose
프로젝트 전반에서 사용하는 공통 인프라 모듈. 인증, 권한, 예외 처리, 필터링, 페이지네이션, CRUD 믹스인, 미들웨어 등을 제공한다. Rails의 ApplicationController/Concerns에 해당.

## Key Files

| File | Description |
|------|-------------|
| `apps.py` | Django 앱 설정 (`CoreConfig`) |
| `authentication.py` | `CookieSessionAuthentication` — 세션 쿠키 기반 DRF 인증 백엔드 |
| `exceptions.py` | `JsonApiError`, `NotFound`, 통합 예외 핸들러 (`json_api_exception_handler`) |
| `filters.py` | `create_ransack_filterset()` — Ransack 스타일 동적 필터셋 생성, `AllowedIncludesFilter` |
| `pagination.py` | `JsonApiPageNumberPagination` — JSON:API 페이지네이션 (25/page, max 100) |
| `permissions.py` | `IsAuthenticated`, `IsEnterprise`, `IsPersonal`, `IPBlocklistPermission` |
| `serializers.py` | `ApplicationSerializer` — 기본 JSON:API 시리얼라이저 |
| `throttles.py` | `AuthRateThrottle` — 인증 엔드포인트 rate limiting (10/min) |
| `views.py` | `ApiViewSet` — 기본 ViewSet (JSON:API ModelViewSet + 인증) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `middleware/` | Django 미들웨어 (IP 차단, 현재 유저, 구조화 로깅) (see `middleware/AGENTS.md`) |
| `mixins/` | ViewSet/Serializer 믹스인 (see `mixins/AGENTS.md`) |
| `management/` | Django management 커맨드 (see `management/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 새 공통 기능 추가 시 이 앱에 배치
- 모든 ViewSet은 `ApiViewSet`을 상속하고, `CrudActionsMixin`과 함께 사용
- 예외는 `JsonApiError`를 raise — 자동으로 JSON:API 형식으로 응답
- 필터셋은 `create_ransack_filterset(Model, [fields])`로 생성

### Common Patterns
- **Ransack 필터 프리디케이트**: `_eq`, `_not_eq`, `_in`, `_cont`, `_lt`, `_gt`, `_null`, `_not_null`, `_start`, `_end`
- **AllowedIncludesFilter**: ViewSet의 `allowed_includes` 속성으로 허용 include 경로 제어
- **EnumChoiceFilter**: IntegerField + choices 패턴을 문자열 라벨로도 필터링 가능

## Dependencies

### Internal
- `apps.auth_service` — 인증 클라이언트 (authentication.py에서 사용)

### External
- `rest_framework` / `rest_framework_json_api` — DRF 기반
- `django_filters` — 필터링 백엔드

<!-- MANUAL: -->
