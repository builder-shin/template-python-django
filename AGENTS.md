<!-- Generated: 2026-02-28 | Updated: 2026-03-15 -->

# template-python-django

## Purpose
Django REST Framework 기반 JSON:API 템플릿 프로젝트. Convention over Configuration(CoC) 패턴으로 리소스 CRUD를 자동화하며, JWT 인증, Celery 비동기 처리, S3 스토리지를 포함하는 프로덕션 레디 API 백엔드 템플릿.

## Key Files

| File | Description |
|------|-------------|
| `manage.py` | Django CLI 진입점 (기본 settings: `config.settings.development`) |
| `pyproject.toml` | 프로젝트 메타데이터, 의존성, Ruff/pytest/coverage 설정 (Python 3.12, line-length 120) |
| `uv.lock` | uv 패키지 매니저 잠금 파일 |
| `Dockerfile` | Multi-stage 빌드 (Python 3.12-slim digest-pinned, non-root user, 포트 4000, gunicorn) |
| `docker-compose.yml` | PostgreSQL 16 + Redis 7 + Web + Celery + Celery Beat 구성 (리소스 제한 + healthcheck 포함) |
| `gunicorn.conf.py` | Gunicorn 설정 (gthread worker, GUNICORN_WORKERS/GUNICORN_THREADS/GUNICORN_TIMEOUT 환경변수) |
| `Makefile` | 개발 명령어 모음 (`make dev`, `make test`, `make generate` 등) |
| `Procfile.dev` | honcho용 개발 프로세스 정의 (web + celery worker + beat) |
| `.pre-commit-config.yaml` | pre-commit 훅 설정 — Ruff (lint+format), trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, bandit (보안), detect-secrets (시크릿 감지) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `apps/` | Django 애플리케이션 모듈 (see `apps/AGENTS.md`) |
| `config/` | Django 프로젝트 설정 및 라우팅 (see `config/AGENTS.md`) |
| `tests/` | pytest 기반 테스트 스위트 (see `tests/AGENTS.md`) |
| `scripts/` | 셸 스크립트 (setup.sh) (see `scripts/AGENTS.md`) |
| `docs/` | 프로젝트 문서 및 가이드 |

## For AI Agents

### Critical Rules
- **패키지 매니저**: 반드시 `uv`를 사용한다. `pip install` 대신 `uv add`, `pip run` 대신 `uv run`을 사용하라.
- **Make 명령어 우선**: Makefile에 이미 정의된 명령어가 있으면 반드시 `make <target>`을 사용하라. 직접 명령어를 조합하지 마라. (`make test`, `make lint`, `make format`, `make migrate`, `make makemigrations`, `make generate` 등)
- **마이그레이션 파일 직접 생성/수정 금지**: 마이그레이션 파일(.py)을 직접 작성하거나 편집하지 마라. 모델 변경 후 반드시 `make makemigrations`로 자동 생성하고, `make migrate`로 적용하라.

### Working In This Directory
- Python 3.12 필수, uv 패키지 매니저 사용 (`uv sync`, `uv run`)
- JSON:API 스펙 준수 — 모든 응답은 `{ "data": ..., "meta": ..., "links": ... }` 형태
- 한국어 에러 메시지 사용 (사용자 대면 문자열)
- `trailing_slash=False` — URL 끝에 슬래시 없음
- 인증: **JWT Bearer token** (자체 구현, `apps.core.auth`)
- 새 리소스 추가: `make generate name=<복수형> fields="<name>:<Type>"` (`--soft-delete` 옵션으로 SoftDeleteMixin 포함 가능)

### Testing Requirements
- `pytest` 사용, 설정: `config.settings.test`
- 실행: `make test` (권장) 또는 `uv run pytest`
- 커버리지: `make test-cov`, CI에서 최소 80% (`--cov-fail-under=80`)

### Common Patterns
- **CoC 패턴**: ViewSet → serializer_class, queryset, filterset_class 자동 추론 (앱 경로 기반); filterset_class는 각 ViewSet의 allowed_filters dict에서 동적 생성
- **BaseModel**: `created_at`, `updated_at` 타임스탬프, `save()` 시 `full_clean()` 자동 호출
- **SoftDeleteMixin**: 선택적 soft delete. `deleted_at`, `deleted_by_cascade` 필드. `objects`(alive), `all_objects`(전체). FK별 cascade 정책(`SOFT_CASCADE`, `HARD_CASCADE_SOFT_CHILDREN`, `SOFT_CASCADE_HARD_CHILDREN`). 모델 상속 시 `SoftDeleteMixin`을 `BaseModel` 앞에 배치
- **HookableSerializerMixin**: 모든 Serializer에 필수 — ViewSet lifecycle hooks 연결
- **ApiViewSet**: 4개 Mixin 합성 (LifecycleHookMixin + UpsertMixin + AutoPrefetchMixin + CoCSerializerMixin + ModelViewSet)
- **IsOwnerOrReadOnly**: `owner_field` 속성으로 소유권 비교 필드 설정 (기본: `"user_id"`, User 모델: `"id"`)
- **URL 패턴**: `api/v1/<resource_name>` (trailing slash 없음)
- **Restore API**: SoftDeleteMixin 모델에 대해 `POST /api/v1/<resource>/{id}/restore` 엔드포인트 자동 제공 (ApiViewSet에 내장)

### Architecture Overview
```
Request → JWTUserMiddleware (structlog용 경량 user)
        → DRF JWTAuthentication (Bearer token 검증 + Redis jti 확인)
        → ApiViewSet = LifecycleHookMixin
                     + UpsertMixin
                     + AutoPrefetchMixin (auto select_related/prefetch_related)
                     + CoCSerializerMixin (auto serializer/filter/queryset)
                     + ModelViewSet
        → HookableSerializerMixin (lifecycle hooks)
        → BaseModel (full_clean on save)
        → JSON:API Response
```

## Dependencies

### External
- Django 5.1, DRF 3.15+, djangorestframework-jsonapi 7.x
- psycopg >=3.1 (PostgreSQL), redis >=5.0
- celery >=5.4, django-celery-beat
- PyJWT 2.x (JWT 인증), boto3 (S3)
- drf-spectacular (OpenAPI), django-structlog (구조화 로깅)
- sentry-sdk (에러 트래킹, production/staging만)
- gunicorn 22 (프로덕션 WSGI)
- django-csp, corsheaders (보안)

<!-- MANUAL: -->
