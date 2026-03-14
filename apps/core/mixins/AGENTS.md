<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-14 -->

# mixins

## Purpose
ApiViewSet을 구성하는 재사용 가능한 클래스 믹스인. CRUD 라이프사이클 훅, CoC 자동 추론, 자동 쿼리 최적화, Upsert, Serializer 훅 브릿지를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 내보내기 — `AutoPrefetchMixin`, `CoCSerializerMixin`, `HookableSerializerMixin`, `LifecycleHookMixin`, `UpsertMixin` |
| `lifecycle_hooks.py` | **LifecycleHookMixin** — CRUD/upsert 라이프사이클 훅 스텁. `create_after_init`, `create_after_save`, `update_after_init`, `update_after_assign`, `update_after_save`, `destroy_after_init`, `destroy_after_save`, `show_after_init`, `new_after_init` |
| `coc_serializer.py` | **CoCSerializerMixin** — 앱 경로 기반 자동 추론. `get_serializer_class()` (serializer), `filterset_class` (allowed_filters dict → 동적 FilterSet), `_infer_included_serializers()` (allowed_includes → included_serializers). 클래스 레벨 캐싱 |
| `auto_prefetch.py` | **AutoPrefetchMixin** — N+1 쿼리 방지. Serializer FK 필드 자동 `select_related`, allowed_includes FK는 `select_related`, 역참조/M2M은 `prefetch_related` (nested select_related 포함). `get_queryset()`, `get_index_scope()` 제공. `select_related_extra`, `prefetch_related_extra` 속성 |
| `upsert.py` | **UpsertMixin** — find-or-create + update. `upsert_find_params()` 오버라이드 필수. Raw `setattr()` 방식 (HookableSerializer 훅 우회). 전용 훅: `upsert_after_init`, `upsert_after_assign`, `upsert_after_save(instance, success, created)`. `transaction.atomic` + `select_for_update` |
| `crud_actions.py` | **HookableSerializerMixin** — DRF serializer.save()와 ViewSet 라이프사이클 훅을 연결. create/update 시 훅 호출, M2M 필드 자동 분리/처리. 모든 Serializer가 첫 번째 부모로 상속 필수 |

## For AI Agents

### Working In This Directory
- **HookableSerializerMixin**: Serializer 선언 시 반드시 첫 번째 부모로 지정 — `class MySerializer(HookableSerializerMixin, serializers.ModelSerializer)`
- **Mixin 합성 순서** (MRO): `LifecycleHookMixin → UpsertMixin → AutoPrefetchMixin → CoCSerializerMixin → ModelViewSet`
- **allowed_includes / allowed_filters**: 정적 값 반환 필수 (첫 호출 시 클래스 레벨 캐싱)
- **커스텀 FilterSet**: `_filterset_class`를 ViewSet에 직접 지정하면 CoC 동적 생성 우회

### Hook Flow
```
[Create] Serializer.create() → view.create_after_init(instance) → save → view.create_after_save(instance, success)
[Update] Serializer.update() → setattr → view.update_after_assign(instance) → save → view.update_after_save(instance, success)
[Destroy] ApiViewSet.destroy() → view.destroy_after_init(instance) → delete → view.destroy_after_save(instance, success)
[Upsert] UpsertMixin.upsert() → upsert_after_init → setattr → upsert_after_assign → save → upsert_after_save(instance, success, created)
```

### Auto-Prefetch Strategy
```
1. Serializer ResourceRelatedField 중 FK/OneToOne → auto select_related
2. allowed_includes FK → select_related
3. allowed_includes 역참조/M2M → prefetch_related (nested select_related 포함)
4. select_related_extra / prefetch_related_extra → 수동 추가
```

<!-- MANUAL: -->
