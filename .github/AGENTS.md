<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-02 | Updated: 2026-03-14 -->

# .github

## Purpose
GitHub 설정 — CI/CD 워크플로우, PR 템플릿 등.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `workflows/` | GitHub Actions CI 워크플로우 |

## Key Files

| File | Description |
|------|-------------|
| `workflows/ci.yml` | CI 파이프라인 — lint(Ruff check + format) → test(pytest + coverage, --cov-fail-under=80) with PostgreSQL 16 + Redis 7 |

## For AI Agents

### Working In This Directory
- CI는 `uv`를 패키지 매니저로 사용 (`astral-sh/setup-uv@v4`)
- lint job: `uv run ruff check .` + `uv run ruff format --check .`
- test job: `uv sync --group test` → `uv run pytest --cov=apps --cov-report=term-missing --cov-fail-under=80`
- test 서비스: PostgreSQL 16 (`django_test` DB) + Redis 7
- 트리거: main 브랜치 push 또는 PR
- CI 워크플로우 변경 시 별도 브랜치에서 PR로 검증

<!-- MANUAL: -->
