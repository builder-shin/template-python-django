<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# mixins

## Purpose
Serializer와 ViewSet에서 사용하는 Mixin. HookableSerializerMixin은 ApiViewSet의 라이프사이클 훅을 Serializer에 연결하고, OwnedResourceMixin은 user_id 기반 소유권 검증을 제공.

## Key Files

| File | Description |
|------|-------------|
| `crud_actions.py` | `HookableSerializerMixin` — Serializer의 create/update 시 ApiViewSet 라이프사이클 훅 호출 브릿지 |
| `owned_resource.py` | `OwnedResourceMixin` — user_id 기반 소유권 검증 (create_after_init에서 자동 설정, update/destroy_after_init에서 검증) |

## For AI Agents

### Working In This Directory
- **HookableSerializerMixin**: ApiViewSet과 반드시 함께 사용 — create/update 시 라이프사이클 훅 호출
  - Create: `create_after_init(instance)` → `save()` → `create_after_save(instance, success)`
  - Update: `update_after_assign(instance)` → `save()` → `update_after_save(instance, success)`
- **OwnedResourceMixin**: ViewSet에 추가 상속하여 소유권 검증 자동화
  - `owner_field` (기본 "user_id"), `resource_label` (기본 "리소스") 오버라이드 가능
  - `create_after_init`: request.user.id를 owner_field에 자동 설정
  - `update_after_init`, `destroy_after_init`: 소유권 검증 실패 시 403 JsonApiError
- CRUD 라이프사이클 훅 자체는 `apps.core.views.ApiViewSet`에 정의됨 (이 디렉토리가 아님)
- 훅에서 중단하려면 `raise JsonApiError(...)` — Response 직접 반환 금지

### Testing Requirements
- `tests/core/test_crud_actions.py`에서 HookableSerializerMixin 동작 테스트

<!-- MANUAL: -->
