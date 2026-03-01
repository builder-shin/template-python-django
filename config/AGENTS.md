<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# config

## Purpose
Django 프로젝트 설정, URL 라우팅, WSGI/ASGI 진입점, Celery 설정을 담당하는 프로젝트 구성 패키지.

## Key Files

| File | Description |
|------|-------------|
| `urls.py` | URL 라우팅 — health check, API v1 엔드포인트, Swagger UI, debug toolbar |
| `celery.py` | Celery 앱 초기화 (autodiscover_tasks, Django settings 연동) |
| `wsgi.py` | WSGI 진입점 (gunicorn 사용) |
| `asgi.py` | ASGI 진입점 (비동기 지원) |
| `__init__.py` | Celery app import (`from .celery import app as celery_app`) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `settings/` | 환경별 분리된 Django 설정 (see `settings/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- URL 추가 시 `urlpatterns`에 `path("api/v1/", include("apps.<name>.urls"))` 형태로 등록
- `# API v1 endpoints` 주석 아래에 새 앱 URL 등록 (generate_resource 명령어가 자동 등록)
- Health check 엔드포인트: `/health/live`, `/health/ready` (인증 불필요)
- Swagger UI: `/api-docs/`, Schema: `/api/schema/`

### Testing Requirements
- URL 라우팅은 통합 테스트에서 검증
- Celery 태스크는 테스트 시 `CELERY_TASK_ALWAYS_EAGER=True`로 동기 실행

### Common Patterns
- DEBUG 모드에서만 django-debug-toolbar URL 등록
- Celery autodiscover로 앱 내 tasks.py 자동 탐지

## Dependencies

### Internal
- `apps/members/urls` — Members API 엔드포인트
- `apps/posts/urls` — Posts API 엔드포인트
- `apps/comments/urls` — Comments API 엔드포인트

### External
- drf-spectacular — OpenAPI 스키마 생성
- debug_toolbar — 디버그 툴바 (개발 환경)

<!-- MANUAL: -->
