<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# tests/posts

## Purpose
Post 도메인 테스트. 모델 유효성 검증, 상태 전환, API 엔드포인트 통합 테스트.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `test_models.py` | Post 모델 테스트 — 상태 전환, publish/archive, 유효성 검증, QuerySet |
| `test_api.py` | Posts API 테스트 — CRUD, publish, upsert, 권한, 필터링, JSON:API 형식 |

## For AI Agents

### Working In This Directory
- publish 워크플로우: DRAFT → PUBLISHED (content 필수)
- upsert: external_id 기반 — 존재하면 업데이트, 없으면 생성
- `get_index_scope`가 본인 글만 반환하는지 검증
- conftest.py의 인증 fixture 활용

<!-- MANUAL: -->
