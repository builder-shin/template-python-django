<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-14 -->

# settings

## Purpose
환경별 Django 설정. base.py를 공유하고 환경별 파일에서 오버라이드한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `base.py` | **공통 설정** — INSTALLED_APPS, MIDDLEWARE, REST_FRAMEWORK(JSON:API), DATABASES(PostgreSQL), CACHES(Redis), Celery, CORS, JWT_AUTH, Sentry, CSP, S3, Logging |
| `development.py` | 개발 환경 — DEBUG=True, django-debug-toolbar, 완화된 보안 설정 |
| `production.py` | 프로덕션 환경 — DEBUG=False, 강화된 보안 (HSTS, SSL redirect), Sentry 활성화, `SECURE_REDIRECT_EXEMPT = [r"^health/"]` (health check SSL 제외) |
| `test.py` | 테스트 환경 — 빠른 실행을 위한 간소화 설정 |

## For AI Agents

### Working In This Directory
- 새 앱 등록: `base.py`의 `# Local apps` 주석 아래에 AppConfig 추가
- 환경변수: `.env` 파일 → `python-dotenv`로 로드
- REST_FRAMEWORK 설정: JSON:API 파서/렌더러, 페이지네이션, 예외 핸들러, JWT 인증, 스로틀링
- JSON_API_FORMAT_FIELD_NAMES = "underscore", JSON_API_PLURALIZE_TYPES = True
- APPEND_SLASH = False (trailing_slash=False와 일치)
- production.py: health check 경로는 SSL redirect에서 제외 (`SECURE_REDIRECT_EXEMPT`)

### Key Settings
```python
AUTH_USER_MODEL = "users.User"
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
PAGE_SIZE = 25
THROTTLE_RATES: anon=300/5min, user=300/5min, auth=10/min
JWT_AUTH = {
    ACCESS_TOKEN_LIFETIME_SECONDS: 900,   # 15분
    REFRESH_TOKEN_LIFETIME_SECONDS: 604800,  # 7일
    ALGORITHM: "HS256",
    ROTATE_REFRESH_TOKENS: True,
}
```

<!-- MANUAL: -->
