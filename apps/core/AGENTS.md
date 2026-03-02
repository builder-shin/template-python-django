<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# core

## Purpose
프로젝트 공통 인프라. ApiViewSet(CRUD 라이프사이클 훅 + CoC 자동 추론), 예외 처리, 필터, 미들웨어, 믹스인, 유틸리티를 제공한다. 모든 도메인 앱이 이 모듈에 의존한다.

## Key Files

| File | Description |
|------|-------------|
| `views.py` | **ApiViewSet** — ModelViewSet 기반, CRUD 라이프사이클 훅 + CoC 자동 추론 (serializer_class, filterset_class, included_serializers). health_live/health_ready 엔드포인트 포함 |
| `exceptions.py` | **JsonApiError**, **NotFound** 커스텀 예외 + `json_api_exception_handler` 통합 핸들러 (한국어 메시지) |
| `filters.py` | **AllowedIncludesFilter** — JSON:API `?include=` 경로 화이트리스트 필터 백엔드 |
| `pagination.py` | **JsonApiPageNumberPagination** — page[number]/page[size] 파라미터, total-count 메타 |
| `utils.py` | `get_client_ip`, `singularize` (inflect 기반), `to_pascal` 유틸리티 |
| `authentication.py` | DRF 내장 인증 사용 문서 (SessionAuthentication + TokenAuthentication) |
| `permissions.py` | DRF 내장 IsAuthenticated 사용 문서 |
| `throttles.py` | **AuthRateThrottle** — 인증 엔드포인트 10/min 제한 |
| `apps.py` | CoreConfig 앱 설정 |
| `urls.py` | Core URL 라우팅 |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `middleware/` | HTTP 미들웨어 — IP 차단 (see `middleware/AGENTS.md`) |
| `management/` | Django 관리 명령어 (see `management/AGENTS.md`) |
| `mixins/` | 재사용 가능한 클래스 믹스인 (see `mixins/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- **ApiViewSet 수정 시 주의**: 모든 도메인 앱이 의존하므로 하위 호환성 유지 필수
- **CoC 자동 추론**: `get_serializer_class()`, `filterset_class` property, `_maybe_inject_included_serializers()`가 앱 경로(apps.{app_label})에서 자동으로 Serializer/Filter/IncludedSerializers를 찾음
- **라이프사이클 훅 체인**: create/update 훅은 HookableSerializerMixin이 호출, destroy/show/new/upsert 훅은 ApiViewSet이 직접 호출
- **예외 처리**: 모든 커스텀 에러는 `JsonApiError(title, detail, status_code)`로 발생
- **CoC 네이밍 규칙**: `{SingularPascal}Serializer`, `{SingularPascal}Filter` (singularize + to_pascal 사용)

### Testing Requirements
- views.py 변경 시 `tests/core/test_coc_inference.py` + `tests/core/test_crud_actions.py` 실행
- 새 필터 백엔드 추가 시 통합 테스트 필수

### Key Architecture: CoC Auto-Inference
```
ViewSet._get_app_label() → "posts"
  → singularize("posts") → "post"
  → to_pascal("post") → "Post"
  → get_serializer_class() → apps.posts.serializers.PostSerializer
  → filterset_class → apps.posts.filters.PostFilter
  → _infer_included_serializers() → allowed_includes + model introspection
```

<!-- MANUAL: -->
