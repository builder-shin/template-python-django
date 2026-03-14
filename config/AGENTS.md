<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-14 -->

# config

## Purpose
Django 프로젝트 설정 모듈. WSGI/ASGI 진입점, 루트 URL 라우팅, Celery 설정, 환경별 설정을 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 — Celery app import (`from .celery import app as celery_app`) |
| `urls.py` | 루트 URL 라우팅 — health 체크 (`apps.core.health`), API v1 엔드포인트, Swagger UI (DEBUG), debug toolbar (DEBUG). schema/docs에 trailing-slash 없는 variants 포함 |
| `wsgi.py` | WSGI 진입점 (Gunicorn용) |
| `asgi.py` | ASGI 진입점 |
| `celery.py` | Celery 앱 설정 및 autodiscover |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `settings/` | 환경별 설정 (base, development, production, test) (see `settings/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 새 앱 URL 등록: `urls.py`의 `# API v1 endpoints` 주석 아래에 추가
- URL 패턴: `path("api/v1/", include("apps.{name}.urls"))`
- health 엔드포인트: `apps.core.health` 모듈의 함수 뷰 (`health_live`, `health_ready`)
- Swagger UI: `/api-docs/` (DEBUG 모드 전용), trailing-slash 없는 `/api-docs` variant도 등록
- DEBUG 모드에서만 django-debug-toolbar 활성화

### URL Structure
```
/health/live          → health_live (단순 생존 체크)
/health/ready         → health_ready (DB + 캐시 연결 체크)
/api/v1/users         → UsersViewSet
/api/v1/posts         → PostsViewSet
/api/v1/comments      → CommentsViewSet
/api/v1/auth/login    → LoginView (JWT)
/api/v1/auth/refresh  → RefreshView (JWT)
/api/v1/auth/logout   → LogoutView (JWT)
/api/v1/auth/logout-all → LogoutAllView (JWT)
/api/schema/          → OpenAPI 스키마 (DEBUG)
/api/schema           → OpenAPI 스키마 no-slash (DEBUG)
/api-docs/            → Swagger UI (DEBUG)
/api-docs             → Swagger UI no-slash (DEBUG)
```

## Dependencies

### Internal
- `apps/users/urls` — Users API
- `apps/posts/urls` — Posts API
- `apps/comments/urls` — Comments API
- `apps/core/auth/urls` — JWT Auth API
- `apps/core/health` — Health check endpoints

### External
- drf-spectacular — OpenAPI 스키마 생성
- debug_toolbar — 디버그 툴바 (개발 환경)

<!-- MANUAL: -->
