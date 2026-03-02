<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# template-python-django

## Purpose
Django REST Framework API 템플릿 프로젝트. JSON:API 스펙을 준수하는 RESTful API 서버로, Django 내장 인증 시스템(Session + Token)을 사용하며 Posts/Comments/Members 도메인을 제공한다. Rails CrudActions 패턴을 Django에 이식한 구조.

## Key Files

| File | Description |
|------|-------------|
| `manage.py` | Django CLI 진입점 (기본 settings: `config.settings.development`) |
| `pyproject.toml` | 프로젝트 메타데이터, 의존성, Ruff/pytest/coverage 설정 (Python 3.12, line-length 120) |
| `uv.lock` | uv 패키지 매니저 잠금 파일 |
| `Dockerfile` | Multi-stage 빌드 (Python 3.12-slim, 포트 4000, gunicorn) |
| `docker-compose.yml` | PostgreSQL 16 + Redis 7 + Web + Celery + Celery Beat 구성 |
| `gunicorn.conf.py` | Gunicorn 설정 (gthread worker, 4 workers, 2 threads) |
| `Makefile` | 개발 명령어 모음 (`make dev`, `make test`, `make generate` 등) |
| `Procfile.dev` | honcho용 개발 프로세스 정의 (web + celery worker + beat) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `apps/` | Django 애플리케이션 모듈 (see `apps/AGENTS.md`) |
| `config/` | Django 프로젝트 설정 및 라우팅 (see `config/AGENTS.md`) |
| `tests/` | pytest 기반 테스트 스위트 (see `tests/AGENTS.md`) |
| `scripts/` | 셸 스크립트 (setup.sh) (see `scripts/AGENTS.md`) |
| `.github/` | GitHub Actions CI 워크플로우 (see `.github/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- Python 3.12 필수, uv 패키지 매니저 사용 (`uv sync`, `uv run`)
- `pyproject.toml`에 의존성 및 도구 설정 통합
- JSON:API 스펙 준수 — 모든 응답은 `{ "data": ..., "meta": ..., "links": ... }` 형태
- 한국어 에러 메시지 사용 (사용자 대면 문자열)
- Rails 패턴 이식 프로젝트 — CrudActions, django-filter, Current 등
- `trailing_slash=False` — URL 끝에 슬래시 없음

### Testing Requirements
- `pytest` 사용, 설정: `config.settings.test`
- 실행: `pytest` (루트에서) 또는 `make test`
- 커버리지: `pytest --cov=apps --cov-report=term-missing` (최소 80%)
- markers: `@pytest.mark.slow`

### Common Patterns
- **ApiViewSet + HookableSerializerMixin**: ViewSet에 CRUD 라이프사이클 훅 내장, Serializer는 HookableSerializerMixin으로 훅 연결
- **django-filter FilterSet**: 표준 `django_filters.FilterSet` 클래스 사용 (`exact`, `icontains`, `gt`, `lt` 등)
- **내장 인증**: Django 내장 인증 시스템 (SessionAuthentication + TokenAuthentication)
- **AllowedIncludesFilter**: JSON:API `?include=` 경로 화이트리스트 제어
- **코드 생성기**: `make generate name=resources fields="name:CharField"` 로 리소스 스캐폴딩

### Architecture Overview
```
Client → Django (Gunicorn) → DRF JSON:API
           ↓                      ↓
    Session/TokenAuth         ApiViewSet
    (DRF 내장 인증)         (CRUD + 라이프사이클 훅)
           ↓                      ↓
    Redis (캐시/Celery)     HookableSerializerMixin
    PostgreSQL (데이터)
```

## Dependencies

### External
- Django 5.x — 웹 프레임워크
- djangorestframework + djangorestframework-jsonapi — JSON:API 직렬화
- django-filter — 쿼리 필터링
- Celery + django-celery-beat — 비동기 태스크/스케줄링
- Redis — 캐시 및 Celery 브로커
- PostgreSQL 16 — 주 데이터베이스
- Sentry — 에러 모니터링 (production/staging)
- SendGrid — 이메일 발송
- drf-spectacular — OpenAPI/Swagger 문서
- django-storages + boto3 — AWS S3 파일 스토리지
- django-csp — Content Security Policy

<!-- MANUAL: -->
