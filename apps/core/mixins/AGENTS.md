<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# mixins

## Purpose
ViewSet과 Serializer에서 사용하는 CRUD 라이프사이클 훅 Mixin. Rails CrudActions concern을 Django에 이식.

## Key Files

| File | Description |
|------|-------------|
| `crud_actions.py` | `CrudActionsMixin` (ViewSet용) + `HookableSerializerMixin` (Serializer용) |

## For AI Agents

### Working In This Directory
- **CrudActionsMixin**: list, retrieve, create, update, partial_update, destroy, new, upsert 액션 제공
- **HookableSerializerMixin**: 반드시 CrudActionsMixin과 함께 사용 — create/update 시 라이프사이클 훅 호출
- 라이프사이클 훅 순서:
  - Create: `create_after_init(instance)` → `save()` → `create_after_save(instance, success)`
  - Update: `update_after_init(instance)` → `update_after_assign(instance)` → `save()` → `update_after_save(instance, success)`
  - Destroy: `destroy_after_init(instance)` → `delete()` → `destroy_after_save(instance, success)`
  - Upsert: `upsert_after_init` → `upsert_after_assign` → `save()` → `upsert_after_save(instance, success, created)`
- 훅에서 중단하려면 `raise JsonApiError(...)` — Response 직접 반환 금지
- `get_object()` 오버라이드: DRF 기본 대신 `NotFound()` (JSON:API 포맷) 발생
- `get_index_scope()`: 리스트 조회 시 기본 쿼리셋 커스터마이징
- `allowed_includes` 프로퍼티: JSON:API `?include=` 허용 경로 목록

### Testing Requirements
- `tests/core/test_crud_actions.py`에서 Mixin 동작 테스트

<!-- MANUAL: -->
