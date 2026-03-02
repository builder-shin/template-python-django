<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# mixins

## Purpose
재사용 가능한 클래스 믹스인. CRUD 라이프사이클 훅 브릿지와 사용자 소유권 검증을 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 내보내기 — `UserScopedMixin` |
| `crud_actions.py` | **HookableSerializerMixin** — DRF serializer.save()와 ApiViewSet 라이프사이클 훅을 연결. create/update 시 훅 호출, M2M 필드 자동 처리. 모든 Serializer가 첫 번째 부모로 상속 필수 |
| `user_scoped.py` | **UserScopedMixin** — user_id 기반 소유권 검증. create_after_init(자동 user_id 할당), update_after_init(수정 권한 체크), destroy_after_init(삭제 권한 체크). resource_label로 에러 메시지 커스터마이즈 |

## For AI Agents

### Working In This Directory
- **HookableSerializerMixin**: Serializer 선언 시 반드시 첫 번째 부모로 지정 — `class MySerializer(HookableSerializerMixin, serializers.ModelSerializer)`
- **UserScopedMixin**: ViewSet 선언 시 ApiViewSet 앞에 지정 — `class MyViewSet(UserScopedMixin, ApiViewSet)`
- **resource_label**: ViewSet 클래스에서 오버라이드하여 한국어 에러 메시지 커스터마이즈 (예: `resource_label = "글"`)
- MRO 순서 중요: Mixin → ApiViewSet 순서로 상속

### Hook Flow
```
[Create] Serializer.create() → view.create_after_init(instance) → save → view.create_after_save(instance, success)
[Update] Serializer.update() → setattr → view.update_after_assign(instance) → save → view.update_after_save(instance, success)
[Destroy] ApiViewSet.destroy() → view.destroy_after_init(instance) → delete → view.destroy_after_save(instance, success)
```

<!-- MANUAL: -->
