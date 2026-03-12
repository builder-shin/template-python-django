<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-12 -->

# tests/posts

## Purpose
Post 도메인 테스트. 모델 단위 테스트와 API 통합 테스트를 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `test_models.py` | Post 모델 테스트 — 생성, 유효성 검증(발행 상태 content 필수, 미래 published_at 불가), title strip, unique per user |
| `test_api.py` | Post API 테스트 — CRUD, 인증, 소유권, upsert(external_id), JSON:API 필터/정렬/include |
| `test_validation.py` | Post 유효성 검증 테스트 — 발행 상태 content 필수, 미래 published_at 불가, title strip 등 |
| `test_filters.py` | Post 필터 테스트 — allowed_filters dict 기반 필터링 (status, title 등) |
| `test_pagination.py` | Post 페이지네이션 테스트 — page[number]/page[size] 파라미터 검증 |

## For AI Agents

### Working In This Directory
- `mock_authenticated` fixture로 인증 사용자 생성
- `jsonapi_payload()` 헬퍼로 JSON:API 요청 본문 생성
- upsert 테스트: external_id 기반 생성/업데이트
- get_index_scope: 인증된 사용자는 자기 글만 조회

<!-- MANUAL: -->
