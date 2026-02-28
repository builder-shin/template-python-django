<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# tests/members

## Purpose
Member 도메인 테스트. 모델 유효성 검증 및 API 엔드포인트 통합 테스트.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `test_models.py` | Member 모델 테스트 — 유효성 검증, 상태 전환, QuerySet |
| `test_api.py` | Members API 테스트 — CRUD, me 액션, 권한, JSON:API 형식 |

## For AI Agents

### Working In This Directory
- `user_id` unique 제약 테스트 포함
- `me` 커스텀 액션 테스트
- conftest.py의 인증 fixture 활용

<!-- MANUAL: -->
