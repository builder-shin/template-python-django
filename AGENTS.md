<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# template-python-django

## Purpose
Django REST Framework API 템플릿 프로젝트. JSON:API 스펙을 준수하는 RESTful API 서버로, 외부 인증 서비스와 연동하며 Posts/Comments/Members 도메인을 제공한다. Rails CrudActions 패턴을 Django에 이식한 구조.

## Key Files

| File | Description |
|------|-------------|
| `manage.py` | Django CLI 진입점 (기본 settings: `config.settings.development`) |
| `pyproject.toml` | 프로젝트 메타데이터, Black/Ruff/pytest 설정 (Python 3.12, line-length 120) |
| `Dockerfile` | Multi-stage 빌드 (Python 3.12-slim, 포트 4000, gunicorn) |
| `docker-compose.yml` | PostgreSQL 16 + Redis 7 + Web + Celery + Celery Beat 구성 |
| `gunicorn.conf.py` | Gunicorn 설정 (gthread worker, 4 workers, 2 threads) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `apps/` | Django 애플리케이션 모듈 (see `apps/AGENTS.md`) |
| `config/` | Django 프로젝트 설정 및 라우팅 (see `config/AGENTS.md`) |
| `requirements/` | pip 의존성 파일 (see `requirements/AGENTS.md`) |
| `tests/` | pytest 기반 테스트 스위트 (see `tests/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- Python 3.12 필수, `pyproject.toml`에 도구 설정 통합
- JSON:API 스펙 준수 — 모든 응답은 `{ "data": ..., "meta": ..., "links": ... }` 형태
- 한국어 에러 메시지 사용 (사용자 대면 문자열)
- Rails 패턴 이식 프로젝트 — CrudActions, Ransack 필터, Current 등

### Testing Requirements
- `pytest` 사용, 설정: `config.settings.test`
- 실행: `pytest` (루트에서)
- markers: `@pytest.mark.slow`

### Common Patterns
- **CrudActionsMixin + HookableSerializerMixin**: ViewSet과 Serializer에서 라이프사이클 훅 패턴
- **Ransack-style 필터**: `create_ransack_filterset()`으로 동적 필터셋 생성 (`_eq`, `_cont`, `_gt` 등)
- **외부 인증**: `AuthServiceClient`로 세션 쿠키 기반 인증, `AuthUser` dataclass 사용
- **AllowedIncludesFilter**: JSON:API `?include=` 경로 화이트리스트 제어

### Architecture Overview
```
Client → Django (Gunicorn) → DRF JSON:API
           ↓                      ↓
    CookieSessionAuth       CrudActionsMixin
           ↓                      ↓
    AuthServiceClient       HookableSerializer
    (외부 인증 서비스)        (라이프사이클 훅)
           ↓
    Redis (캐시/Celery)
    PostgreSQL (데이터)
```

## Dependencies

### External
- Django 5.x — 웹 프레임워크
- djangorestframework + djangorestframework-jsonapi — JSON:API 직렬화
- django-filter — 쿼리 필터링
- httpx — 인증 서비스 HTTP 클라이언트
- Celery + django-celery-beat — 비동기 태스크/스케줄링
- Redis — 캐시 및 Celery 브로커
- PostgreSQL 16 — 주 데이터베이스
- Sentry — 에러 모니터링 (production/staging)
- SendGrid — 이메일 발송
- drf-spectacular — OpenAPI/Swagger 문서
- django-storages + boto3 — AWS S3 파일 스토리지

<!-- MANUAL: -->
