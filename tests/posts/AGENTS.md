<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# posts

## Purpose
Post 모델 유효성 및 API 엔드포인트 테스트.

## Key Files

| File | Description |
|------|-------------|
| `test_models.py` | Post 모델 테스트 — 생성, publish/archive, 유효성(published 시 content 필수), view_count, summary |
| `test_api.py` | Posts API 테스트 — CRUD, publish 액션, upsert, include=comments, 권한 |

## For AI Agents

### Working In This Directory
- PostFactory 사용하여 테스트 데이터 생성
- publish 테스트: draft 상태에서만 발행 가능, content 필수
- upsert 테스트: external_id 기반 find-or-create

<!-- MANUAL: -->
