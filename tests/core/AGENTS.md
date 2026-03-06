<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-06 -->

# tests/core

## Purpose
Core 인프라 테스트. CoC 자동 추론, CrudActions 라이프사이클 훅, JWT 인증을 검증한다.

## Key Files

| File | Description |
|------|-------------|
| `test_coc_inference.py` | **CoC 추론 테스트** — serializer_class, filterset_class, included_serializers 자동 추론, 캐싱, 에러 케이스 |
| `test_crud_actions.py` | **CrudActions 테스트** — create/update/destroy 라이프사이클 훅 호출 순서, HookableSerializerMixin 동작, M2M 필드 처리 |
| `test_auth.py` | **JWT 인증 테스트** — login, refresh (토큰 로테이션), logout, logout-all, 토큰 만료/무효화 |

## For AI Agents

### Working In This Directory
- CoC 테스트: Mock ViewSet/Serializer로 자동 추론 로직 검증
- CrudActions 테스트: 훅 호출 여부 및 순서 검증
- Auth 테스트: JWT 토큰 생성/검증/무효화 흐름 검증
- `apps/core/views.py` 변경 시 반드시 이 테스트 실행

<!-- MANUAL: -->
