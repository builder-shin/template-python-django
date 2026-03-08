<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-08 -->

# migrations (posts)

## Purpose
Post 모델의 Django 데이터베이스 마이그레이션 파일.

## For AI Agents

### Working In This Directory
- **마이그레이션 파일을 직접 생성하거나 수정하지 마라.** 모델 변경 후 반드시 `make makemigrations`로 자동 생성하고, `make migrate`로 적용하라.
- 앱 단위 생성이 필요하면: `uv run python manage.py makemigrations posts`
- Ruff/린트 제외 대상 (pyproject.toml per-file-ignores)

<!-- MANUAL: -->
