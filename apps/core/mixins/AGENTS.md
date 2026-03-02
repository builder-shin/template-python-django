<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# mixins

## Purpose
Serializer에서 사용하는 Mixin. HookableSerializerMixin은 ApiViewSet의 라이프사이클 훅을 Serializer에 연결.

## Key Files

| File | Description |
|------|-------------|
| `crud_actions.py` | `HookableSerializerMixin` — Serializer의 create/update 시 ApiViewSet 라이프사이클 훅 호출 브릿지 |

## For AI Agents

### Working In This Directory
- **HookableSerializerMixin**: ApiViewSet과 반드시 함께 사용 — create/update 시 라이프사이클 훅 호출
  - Create: `create_after_init(instance)` → `save()` → `create_after_save(instance, success)`
  - Update: `update_after_assign(instance)` → `save()` → `update_after_save(instance, success)`
- 소유권 검증은 각 ViewSet에서 직접 구현 (`_check_ownership`, `create_after_init` 등)
- CRUD 라이프사이클 훅 자체는 `apps.core.views.ApiViewSet`에 정의됨 (이 디렉토리가 아님)
- 훅에서 중단하려면 `raise JsonApiError(...)` — Response 직접 반환 금지

### Testing Requirements
- `tests/core/test_crud_actions.py`에서 HookableSerializerMixin 동작 테스트

<!-- MANUAL: -->
