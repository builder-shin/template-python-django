<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# migrations

## Purpose
Posts 앱 Django 데이터베이스 마이그레이션 파일.

## Key Files

| File | Description |
|------|-------------|
| `0001_initial.py` | 초기 마이그레이션 — Post 테이블, status 인덱스, unique_post_title_per_user 제약 |

## For AI Agents

### Working In This Directory
- `make makemigrations` → `make migrate` 순서로 마이그레이션 관리
- 마이그레이션 파일 직접 수정 금지 — `makemigrations`로 재생성

<!-- MANUAL: -->
