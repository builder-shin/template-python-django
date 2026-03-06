<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-06 | Updated: 2026-03-06 -->

# tests/users

## Purpose
User 도메인 테스트. 모델 단위 테스트와 API 통합 테스트를 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `test_models.py` | User 모델 테스트 — 생성, nickname strip, status, __str__ |
| `test_api.py` | User API 테스트 — CRUD, /me 엔드포인트, 권한(자기 프로필만 수정) |

## For AI Agents

### Working In This Directory
- `auth_user` fixture로 테스트 사용자 생성
- `/me` 엔드포인트: 인증된 사용자만 접근 가능
- 프로필 수정: 본인만 가능 (IsOwnerUser 권한)

<!-- MANUAL: -->
