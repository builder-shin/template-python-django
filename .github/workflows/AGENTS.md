<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-06 | Updated: 2026-03-14 -->

# workflows

## Purpose
GitHub Actions CI/CD 워크플로우. lint(Ruff) → test(pytest + coverage) 파이프라인을 정의한다.

## Key Files

| File | Description |
|------|-------------|
| `ci.yml` | **CI 파이프라인** — lint job (Ruff check + format) → test job (pytest --cov, --cov-fail-under=80). PostgreSQL 16 + Redis 7 서비스 컨테이너. main 브랜치 push/PR 트리거 |

## For AI Agents

### Working In This Directory
- CI는 `uv` 패키지 매니저 사용 (`astral-sh/setup-uv@v4`)
- lint → test 순서 (`needs: lint`)
- test 환경변수: `DJANGO_SETTINGS_MODULE=config.settings.test`
- 서비스: PostgreSQL 16 (`django_test` DB, postgres/postgres), Redis 7
- Python 3.12 사용
- 커버리지 최소 80% 필수 (`--cov-fail-under=80`)
- 워크플로우 변경 시 별도 브랜치에서 PR로 검증 권장

### Pipeline Structure
```
[push/PR to main]
  └── lint (ubuntu-latest)
       ├── ruff check .
       └── ruff format --check .
           └── test (ubuntu-latest, needs: lint)
                ├── services: postgres:16, redis:7
                ├── uv sync --group test
                └── pytest --cov=apps --cov-report=term-missing --cov-fail-under=80
```

<!-- MANUAL: -->
