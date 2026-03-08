<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-08 -->

# tests/comments

## Purpose
Comment 도메인 테스트. 모델 단위 테스트와 API 통합 테스트를 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `test_models.py` | Comment 모델 테스트 — 생성, 대댓글, 유효성 검증(다른 글의 댓글 parent 불가) |
| `test_api.py` | Comment API 테스트 — CRUD, 인증, 소유권, include=post, 필터, 발행된 글만 댓글 가능 |

## For AI Agents

### Working In This Directory
- Comment는 Post에 의존 — 테스트 데이터에 Post 먼저 생성 필요
- 대댓글 테스트: parent가 같은 post의 댓글인지 검증
- validate_post: PUBLISHED 상태가 아닌 게시글에 댓글 시 ValidationError

<!-- MANUAL: -->
