<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# tests/members

## Purpose
Member 도메인 테스트. 모델 단위 테스트와 API 통합 테스트를 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `test_models.py` | Member 모델 테스트 — 생성, 상태 변경(suspend/withdraw), nickname strip |
| `test_api.py` | Member API 테스트 — CRUD, 인증, 소유권, /me 엔드포인트 |

## For AI Agents

### Working In This Directory
- `/me` 엔드포인트: 인증 사용자의 Member 프로필 반환 테스트
- user_id unique 제약 조건 테스트

<!-- MANUAL: -->
