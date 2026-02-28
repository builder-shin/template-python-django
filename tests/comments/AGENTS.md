<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# tests/comments

## Purpose
Comment 도메인 테스트. 모델 유효성 검증 및 API 엔드포인트 통합 테스트.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `test_models.py` | Comment 모델 테스트 — 유효성 검증, 대댓글 규칙, QuerySet |
| `test_api.py` | Comments API 테스트 — CRUD, 권한, include, JSON:API 형식 |

## For AI Agents

### Working In This Directory
- 대댓글 테스트: parent가 다른 post에 속할 때 ValidationError 확인
- API 테스트: JSON:API 형식 request body (`{ "data": { "type": "comments", "attributes": {...} } }`)
- conftest.py의 인증 fixture 활용

<!-- MANUAL: -->
