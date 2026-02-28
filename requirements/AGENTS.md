<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# requirements

## Purpose
pip 의존성 관리 파일. 환경별로 분리되어 있으며, base를 상속하는 구조.

## Key Files

| File | Description |
|------|-------------|
| `base.txt` | 프로덕션 의존성 (Django, DRF, JSON:API, httpx, Celery, Sentry 등) |
| `dev.txt` | 개발 의존성 — base.txt 포함 + Black, Ruff, django-debug-toolbar |
| `test.txt` | 테스트 의존성 — base.txt 포함 + pytest, pytest-django, factory-boy, freezegun |

## For AI Agents

### Working In This Directory
- 새 패키지 추가 시 적절한 파일에 추가 (프로덕션: `base.txt`, 개발만: `dev.txt`, 테스트만: `test.txt`)
- `dev.txt`와 `test.txt`는 첫 줄에 `-r base.txt`로 base를 포함
- Dockerfile은 `base.txt`만 설치

<!-- MANUAL: -->
