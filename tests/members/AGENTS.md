<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# members

## Purpose
Member 모델 유효성 및 API 엔드포인트 테스트.

## Key Files

| File | Description |
|------|-------------|
| `test_models.py` | Member 모델 테스트 — 생성, 상태 변경(suspend/withdraw), nickname strip, 유효성 |
| `test_api.py` | Members API 테스트 — CRUD, /me 액션, 권한(본인 프로필만 수정/삭제) |

## For AI Agents

### Working In This Directory
- MemberFactory 사용하여 테스트 데이터 생성
- Status IntegerChoices: 0=active, 1=suspended, 2=withdrawn

<!-- MANUAL: -->
