<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# core

## Purpose
프로젝트 전체에서 사용하는 공통 기반 모듈. 인증, 예외 처리, 필터, 페이지네이션, 퍼미션, 스로틀링, 미들웨어, Mixin, 관리 명령어를 제공.

## Key Files

| File | Description |
|------|-------------|
| `authentication.py` | 인증 설정 안내 — DRF 내장 SessionAuthentication + TokenAuthentication 사용 |
| `exceptions.py` | `JsonApiError`, `NotFound`, 통합 예외 핸들러 (JSON:API 포맷, 한국어 메시지) |
| `filters.py` | `create_ransack_filterset()` — Ransack 스타일 동적 필터셋 생성기, `AllowedIncludesFilter`, `EnumChoiceFilter` |
| `serializers.py` | `ApplicationSerializer` — 모든 시리얼라이저의 베이스 클래스 |
| `pagination.py` | `JsonApiPageNumberPagination` — page[number]/page[size] + total-count 메타 |
| `permissions.py` | `IsAuthenticated`, `IPBlocklistPermission` |
| `throttles.py` | `AuthRateThrottle` — 인증 엔드포인트 전용 (10/min) |
| `views.py` | `ApiViewSet` — 인증 포함 기본 ViewSet (JSON:API ModelViewSet 상속) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `middleware/` | 커스텀 미들웨어 3종 (see `middleware/AGENTS.md`) |
| `mixins/` | CrudActionsMixin + HookableSerializerMixin (see `mixins/AGENTS.md`) |
| `management/` | Django 관리 명령어 (see `management/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 이 앱은 다른 모든 앱의 기반 — 변경 시 전체 영향 분석 필수
- `JsonApiError(title, detail, status_code)`로 예외 발생 — 한국어 detail 필수
- 새 퍼미션 추가 시 `BasePermission` 상속, `has_permission()` 오버라이드
- Ransack 필터 확장 시 `create_ransack_filterset()`에 predicate 추가

### Testing Requirements
- `tests/core/` 에서 CrudActionsMixin 등 통합 테스트
- 미들웨어 변경 시 요청 흐름 전체 테스트 필요

### Common Patterns
- 예외는 항상 `JsonApiError` 또는 DRF 내장 예외 사용 — 직접 Response 반환 금지
- `ApiViewSet` → `IsAuthenticated` 기본 적용
- Ransack 필터 predicate: `_eq`, `_not_eq`, `_in`, `_not_in`, `_cont`, `_not_cont`, `_start`, `_end`, `_lt`, `_lte`, `_gt`, `_gte`, `_null`, `_not_null`, `_matches`

## Dependencies

### External
- rest_framework — DRF 기반
- rest_framework_json_api — JSON:API 직렬화/뷰
- django_filters — 필터 프레임워크

<!-- MANUAL: -->
