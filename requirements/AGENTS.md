<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# requirements

## Purpose
pip 의존성 파일. 환경별 분리: base(공통) → dev(개발 전용) / test(테스트 전용).

## Key Files

| File | Description |
|------|-------------|
| `base.txt` | 공통 의존성 — Django, DRF, JSON:API, psycopg, Celery, Redis, httpx, SendGrid, Sentry, S3, gunicorn 등 |
| `dev.txt` | 개발 전용 — debug-toolbar, ipython, ruff, pre-commit, honcho, django-extensions, inflect |
| `test.txt` | 테스트 전용 — pytest, pytest-django, pytest-cov, factory-boy, faker, respx, freezegun |

## For AI Agents

### Working In This Directory
- dev.txt, test.txt 모두 `-r base.txt`로 base 포함
- 의존성 추가 시 적절한 파일에 추가 (운영 필요 → base, 개발만 → dev, 테스트만 → test)
- 버전 범위: `>=X.Y,<X+1.0` 패턴 사용
- CI에서는 `base.txt + test.txt` 설치

<!-- MANUAL: -->
