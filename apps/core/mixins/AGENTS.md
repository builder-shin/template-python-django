<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-08 -->

# mixins

## Purpose
재사용 가능한 클래스 믹스인. CRUD 라이프사이클 훅 브릿지를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 내보내기 |
| `crud_actions.py` | **HookableSerializerMixin** — DRF serializer.save()와 ApiViewSet 라이프사이클 훅을 연결. create/update 시 훅 호출, M2M 필드 자동 분리/처리. 모든 Serializer가 첫 번째 부모로 상속 필수 |

## For AI Agents

### Working In This Directory
- **HookableSerializerMixin**: Serializer 선언 시 반드시 첫 번째 부모로 지정 — `class MySerializer(HookableSerializerMixin, serializers.ModelSerializer)`

### Hook Flow
```
[Create] Serializer.create() → view.create_after_init(instance) → save → view.create_after_save(instance, success)
[Update] Serializer.update() → setattr → view.update_after_assign(instance) → save → view.update_after_save(instance, success)
[Destroy] ApiViewSet.destroy() → view.destroy_after_init(instance) → delete → view.destroy_after_save(instance, success)
```

<!-- MANUAL: -->
