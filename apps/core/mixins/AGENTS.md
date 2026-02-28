<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# mixins

## Purpose
ViewSet 및 Serializer 믹스인. Rails CrudActions concern을 Django DRF에 이식한 핵심 패턴.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `crud_actions.py` | `CrudActionsMixin` + `HookableSerializerMixin` — 라이프사이클 훅 기반 CRUD |

## For AI Agents

### Working In This Directory
- **CrudActionsMixin** (ViewSet용): list, retrieve, create, update, destroy, new, upsert + 라이프사이클 훅
- **HookableSerializerMixin** (Serializer용): CrudActionsMixin의 훅과 연동하는 create/update 오버라이드
- 두 믹스인은 반드시 함께 사용 — Serializer에 HookableSerializerMixin 없으면 훅 미작동

### Lifecycle Hooks
| Hook | 호출 시점 | 호출 위치 |
|------|----------|----------|
| `create_after_init(instance)` | 모델 인스턴스 생성 후, save 전 | HookableSerializerMixin |
| `create_after_save(instance, success)` | save 후 | HookableSerializerMixin |
| `update_after_init(instance)` | 기존 인스턴스 조회 후 | CrudActionsMixin.update() |
| `update_after_assign(instance)` | 필드 할당 후, save 전 | HookableSerializerMixin |
| `update_after_save(instance, success)` | save 후 | HookableSerializerMixin |
| `destroy_after_init(instance)` | 삭제 대상 조회 후 | CrudActionsMixin.destroy() |
| `destroy_after_save(instance, success)` | delete 후 | CrudActionsMixin.destroy() |
| `show_after_init(instance)` | 조회 인스턴스 로드 후 | CrudActionsMixin.retrieve() |
| `upsert_find_params()` | upsert 조회 키 결정 | CrudActionsMixin.upsert() |

### Common Patterns
- 훅에서 권한 검사: `raise JsonApiError("Forbidden", "...", 403)`
- create_after_init에서 `instance.user_id = self.request.user.id` 패턴
- `get_object()` 오버라이드: DRF 기본 대신 `NotFound` (JSON:API 형식) raise

<!-- MANUAL: -->
