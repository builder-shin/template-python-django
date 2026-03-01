<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# comments

## Purpose
Comment 모델 유효성 및 API 엔드포인트 테스트.

## Key Files

| File | Description |
|------|-------------|
| `test_models.py` | Comment 모델 테스트 — 생성, 대댓글 유효성(같은 post 내), reply_count |
| `test_api.py` | Comments API 테스트 — CRUD, include=post, 권한(본인 댓글만 수정/삭제) |

## For AI Agents

### Working In This Directory
- Comment는 Post 의존 — 테스트 시 PostFactory로 post 먼저 생성
- 대댓글 테스트: parent가 다른 post의 댓글이면 ValidationError

<!-- MANUAL: -->
