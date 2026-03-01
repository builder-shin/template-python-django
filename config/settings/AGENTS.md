<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# settings

## Purpose
환경별 분리된 Django 설정. `base.py`에 공통 설정을 두고 환경별 파일이 이를 오버라이드하는 패턴.

## Key Files

| File | Description |
|------|-------------|
| `base.py` | 공통 설정 — DB, Cache, REST Framework, Celery, CORS, Sentry, CSP, S3, Logging |
| `development.py` | 개발 환경 — DEBUG=True, debug-toolbar, Celery eager, 스로틀링 비활성화 |
| `production.py` | 운영 환경 — SSL/HSTS 설정, 보안 쿠키, health check SSL 제외 |
| `test.py` | 테스트 환경 — LocMemCache, 스로틀링/Sentry 비활성화, MD5 해시 |

## For AI Agents

### Working In This Directory
- 새 앱 등록: `base.py`의 `INSTALLED_APPS` → `# Local apps` 주석 아래에 추가
- 미들웨어 순서 중요: CORS → Security → CSP → Allow2Ban → Common → Session → Auth → django-structlog RequestMiddleware
- `REST_FRAMEWORK` 설정이 JSON:API 전용으로 구성됨 — 파서/렌더러/필터 변경 시 주의
- 환경변수 기본값은 로컬 개발용 (localhost, 기본 포트)
- Sentry는 production/staging에서만 활성화 (`SENTRY_ENABLED_ENVIRONMENTS`)
- `JSON_API_FORMAT_FIELD_NAMES = "underscore"` — 필드명 자동 변환
- `APPEND_SLASH = False` — trailing slash 없음

### Key Configuration
- **인증**: DRF 내장 `SessionAuthentication` + `TokenAuthentication`
- **페이지네이션**: `JsonApiPageNumberPagination` (기본 25, 최대 100)
- **스로틀링**: anon 300/5min, user 300/5min, auth 10/min
- **검색**: `filter[search]` 파라미터
- **DB**: PostgreSQL, `CONN_MAX_AGE=60`, health check 활성화
- **캐시**: Redis (테스트에서는 LocMemCache)
- **보안**: CSP, CORS 허용 오리진, Sentry 민감 데이터 필터링

### Testing Requirements
- 설정 변경 시 test.py에도 필요한 오버라이드 추가
- `CELERY_TASK_ALWAYS_EAGER` — development/test 에서 True

## Dependencies

### Internal
- DRF 내장 `SessionAuthentication` + `TokenAuthentication` — 인증 백엔드
- `apps.core.exceptions.json_api_exception_handler` — 예외 핸들러
- `apps.core.pagination.JsonApiPageNumberPagination` — 페이지네이션
- `apps.core.middleware.allow2ban` — IP 자동 차단 미들웨어
- `django_structlog` — 구조화 로깅 미들웨어 (패키지)

### External
- python-dotenv — `.env` 파일 로딩
- sentry-sdk — 에러 트래킹
- python-json-logger — JSON 로깅 포맷

<!-- MANUAL: -->
