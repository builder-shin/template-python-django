<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# config

## Purpose
Django 프로젝트 설정 모듈. WSGI/ASGI 진입점, 루트 URL 라우팅, Celery 설정, 환경별 설정을 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 — Celery app import (`from .celery import app as celery_app`) |
| `urls.py` | 루트 URL 라우팅 — health 체크, API v1 엔드포인트, Swagger UI, debug toolbar |
| `wsgi.py` | WSGI 진입점 (Gunicorn용) |
| `asgi.py` | ASGI 진입점 (향후 WebSocket 등) |
| `celery.py` | Celery 앱 설정 및 autodiscover |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `settings/` | 환경별 설정 (base, development, production, test) (see `settings/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 새 앱 URL 등록: `urls.py`의 `# API v1 endpoints` 주석 아래에 추가
- URL 패턴: `path("api/v1/", include("apps.{name}.urls"))`
- health 엔드포인트: `/health/live` (단순 OK), `/health/ready` (DB + Cache 체크)
- Swagger UI: `/api-docs/` (개발 환경)
- `trailing_slash=False` — DefaultRouter에서 설정
- DEBUG 모드에서만 django-debug-toolbar 활성화
- Celery autodiscover로 앱 내 tasks.py 자동 탐지

### URL Structure
```
/health/live          → 단순 생존 체크
/health/ready         → DB + 캐시 연결 체크
/api/v1/members       → MembersViewSet
/api/v1/posts         → PostsViewSet
/api/v1/comments      → CommentsViewSet
/api/schema/          → OpenAPI 스키마
/api-docs/            → Swagger UI
```

### Testing Requirements
- URL 라우팅은 통합 테스트에서 검증
- Celery 태스크는 테스트 시 `CELERY_TASK_ALWAYS_EAGER=True`로 동기 실행

## Dependencies

### Internal
- `apps/members/urls` — Members API 엔드포인트
- `apps/posts/urls` — Posts API 엔드포인트
- `apps/comments/urls` — Comments API 엔드포인트

### External
- drf-spectacular — OpenAPI 스키마 생성
- debug_toolbar — 디버그 툴바 (개발 환경)

<!-- MANUAL: -->
