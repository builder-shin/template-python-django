<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-14 -->

# core

## Purpose
프로젝트 공통 인프라. ApiViewSet(4개 mixin 합성: CoC 자동 추론 + Auto Prefetch + Upsert + Lifecycle Hooks), JWT 인증, 예외 처리, 필터, 미들웨어, 믹스인, 유틸리티를 제공한다. 모든 도메인 앱이 이 모듈에 의존한다.

## Key Files

| File | Description |
|------|-------------|
| `views.py` | **ApiViewSet** — `LifecycleHookMixin + UpsertMixin + AutoPrefetchMixin + CoCSerializerMixin + ModelViewSet` 합성. CRUD 액션 + get_object(NotFound) + new 액션 |
| `health.py` | **health_live** (HTTP 200 OK), **health_ready** (DB + Cache 체크, 503 on failure) — 독립 함수 뷰 |
| `exceptions.py` | **JsonApiError**, **NotFound** 커스텀 예외 + `json_api_exception_handler` 통합 핸들러 (401/403/429 한국어 메시지) |
| `filters.py` | **AllowedIncludesFilter** — JSON:API `?include=` 경로 화이트리스트 필터 백엔드. **TIMESTAMP_LOOKUPS** 상수 (`["exact", "gt", "gte", "lt", "lte"]`) |
| `pagination.py` | **JsonApiPageNumberPagination** — page[number]/page[size] 파라미터 |
| `utils.py` | `get_client_ip` (django-ipware), `singularize` (inflect 기반), `to_pascal` 유틸리티 |
| `authentication.py` | **JWTAuthentication** — DRF auth backend, Bearer token 검증 + Redis jti 확인 |
| `permissions.py` | **IsOwnerOrReadOnly** — 객체 소유자만 변경 허용. `owner_field` 속성으로 비교 필드 설정 가능 (기본: `"user_id"`, User 모델은 `"id"`) |
| `throttles.py` | **AuthRateThrottle** — 인증 엔드포인트 IP 기반 10/min 제한 |
| `tasks.py` | **send_notification** — 예제 Celery 태스크. shared_task, bind=True, max_retries=3. config/celery.py에서 autodiscover |
| `urls.py` | `make_urlpatterns()` — URL 보일러플레이트 축소 유틸리티 |
| `apps.py` | CoreConfig |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `auth/` | JWT 인증 — 토큰 생성/검증, Redis 토큰 스토어, login/refresh/logout 뷰 (see `auth/AGENTS.md`) |
| `middleware/` | HTTP 미들웨어 — JWT 유저 추출 (see `middleware/AGENTS.md`) |
| `management/` | Django 관리 명령어 (see `management/AGENTS.md`) |
| `mixins/` | ViewSet 믹스인 — CoC 추론, Auto Prefetch, Lifecycle Hooks, Upsert, HookableSerializer (see `mixins/AGENTS.md`) |
| `models/` | 공통 베이스 모델 (see `models/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- **ApiViewSet 수정 시 주의**: 모든 도메인 앱이 의존하므로 하위 호환성 유지 필수
- **Mixin 합성 순서**: `LifecycleHookMixin → UpsertMixin → AutoPrefetchMixin → CoCSerializerMixin → ModelViewSet` (MRO 순서 중요)
- **CoC 자동 추론**: `get_serializer_class()`, `get_queryset()`, `filterset_class` 모두 앱 경로에서 자동 추론; `filterset_class`는 각 ViewSet의 `allowed_filters` dict에서 동적 생성
- **커스텀 필터**: 기본 `allowed_filters`로 커버되지 않는 경우 `_filterset_class`를 직접 지정
- **소유권 검증**: `IsOwnerOrReadOnly`에서 `owner_field` 속성으로 비교 필드 변경 가능 (User 모델: `owner_field = "id"`)
- **라이프사이클 훅 체인**: create/update 훅은 HookableSerializerMixin이 호출, destroy/show/new 훅은 ApiViewSet이 직접 호출, upsert 훅은 UpsertMixin이 호출
- **예외 처리**: 모든 커스텀 에러는 `JsonApiError(title, detail, status_code)`로 발생

### Testing Requirements
- views.py 변경 시 `tests/core/test_coc_inference.py` + `tests/core/test_crud_actions.py` 실행
- auth 변경 시 `tests/core/test_auth.py` 실행
- health.py 변경 시 `tests/core/test_health.py` 실행

### Key Architecture: Mixin Composition
```
ApiViewSet = LifecycleHookMixin    # CRUD hook stubs (create/update/destroy/show/new)
           + UpsertMixin           # find-or-create + update via raw setattr
           + AutoPrefetchMixin     # auto select_related/prefetch_related from serializer + includes
           + CoCSerializerMixin    # auto serializer_class, filterset_class, included_serializers
           + ModelViewSet          # DRF JSON:API base
```

### CoC Auto-Inference Flow
```
ViewSet._get_app_label() → "posts"
  → singularize("posts") → "post"
  → to_pascal("post") → "Post"
  → get_serializer_class() → apps.posts.serializers.PostSerializer
  → filterset_class → allowed_filters dict → dynamic FilterSet generation
  → get_queryset() → auto select_related/prefetch_related from serializer FK fields + allowed_includes
  → _infer_included_serializers() → allowed_includes + model introspection
```

<!-- MANUAL: -->
