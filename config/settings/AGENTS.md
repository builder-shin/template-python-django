<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# settings

## Purpose
환경별 Django 설정. `base.py`에 공통 설정을 두고, 환경별 파일에서 오버라이드하는 구조.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `base.py` | 공통 설정 — DB, 캐시, REST Framework, JSON:API, Celery, CORS, Sentry, CSP, S3, 로깅 |
| `development.py` | 개발 환경 — DEBUG=True, 추가 개발 도구 |
| `production.py` | 프로덕션 — 보안 강화, HTTPS 설정 |
| `test.py` | 테스트 환경 — 인메모리 캐시, 빠른 비밀번호 해싱 |

## For AI Agents

### Working In This Directory
- `DJANGO_SETTINGS_MODULE` 기본값: `config.settings.development` (manage.py), `config.settings.production` (Dockerfile)
- 새 설정 추가 시 `base.py`에 기본값 포함, 환경별 오버라이드는 해당 파일에
- 환경변수로 설정 주입 (`os.environ.get()`)
- JSON:API 설정: `JSON_API_FORMAT_FIELD_NAMES = "underscore"`, 타입 복수형

### Key Configuration
| Setting | Value | Description |
|---------|-------|-------------|
| DB | PostgreSQL | `DATABASES["default"]` |
| Cache | Redis | `CACHES["default"]` |
| Auth | CookieSession | 외부 인증 서비스 연동 |
| API Format | JSON:API | underscore 필드명, 복수형 타입 |
| Throttle | 300/5min | anon/user rate limit |
| Pagination | 25/page | max 100 |
| Timezone | Asia/Seoul | `TIME_ZONE` |
| Language | ko-kr | `LANGUAGE_CODE` |

<!-- MANUAL: -->
