<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# tests/core

## Purpose
Core 앱 공통 모듈 테스트. CrudActionsMixin 라이프사이클 훅 동작을 검증한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `test_crud_actions.py` | CrudActionsMixin 테스트 — CRUD 훅, upsert, get_object NotFound 등 |

## For AI Agents

### Working In This Directory
- CrudActionsMixin 테스트는 테스트용 모델/ViewSet/Serializer를 fixture로 정의하여 사용
- HookableSerializerMixin과의 연동 테스트 포함

<!-- MANUAL: -->
