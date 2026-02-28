<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# config

## Purpose
Django 프로젝트 설정 모듈. WSGI/ASGI 진입점, URL 라우팅, Celery 설정, 환경별 settings를 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `urls.py` | 루트 URL 라우팅 — health 체크, API v1 엔드포인트, Swagger UI |
| `wsgi.py` | WSGI 애플리케이션 진입점 (Gunicorn용) |
| `asgi.py` | ASGI 애플리케이션 진입점 |
| `celery.py` | Celery 앱 설정 및 autodiscover |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `settings/` | 환경별 Django 설정 (see `settings/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 새 앱의 URL 추가 시 `urls.py`의 `urlpatterns`에 `path("api/v1/", include("apps.xxx.urls"))` 형태로 추가
- Health check 엔드포인트: `GET /health/live`, `GET /health/ready`
- Swagger: `GET /api-docs/`, Schema: `GET /api/schema/`
- `APPEND_SLASH = False` — URL 끝에 슬래시 없음

### API Endpoints
| Path | App |
|------|-----|
| `api/v1/posts` | apps.posts |
| `api/v1/comments` | apps.comments |
| `api/v1/members` | apps.members |

<!-- MANUAL: -->
