<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-06 | Updated: 2026-03-15 -->

# models

## Purpose
공통 베이스 모델, QuerySet, SoftDeleteMixin. 모든 도메인 모델이 상속하는 추상 기본 클래스와 선택적 소프트 삭제 기능을 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | `BaseModel`, `BaseQuerySet`, `SoftDeleteMixin`, `SoftDeleteQuerySet`, `SoftDeleteManager`, `SoftDeleteAllManager`, cascade 정책 상수 내보내기 |
| `base.py` | **BaseModel** — 추상 모델. `created_at`(auto_now_add), `updated_at`(auto_now). `save()` 시 `pre_save()` 호출 후 `full_clean()` 자동 실행 (update_fields 없을 때). **BaseQuerySet** — 도메인 QuerySet의 공통 메서드 제공 |
| `soft_delete.py` | **SoftDeleteMixin** — 선택적 soft delete 추상 Mixin. `deleted_at`, `deleted_by_cascade` 필드. `objects`(alive만), `all_objects`(전체) Manager. `delete()`, `restore()`, `is_deleted` 제공. FK별 cascade 정책: `SOFT_CASCADE`, `HARD_CASCADE_SOFT_CHILDREN`, `SOFT_CASCADE_HARD_CHILDREN` |

## For AI Agents

### Working In This Directory
- 모든 도메인 모델은 `BaseModel`을 상속해야 함
- `save()` 시 자동으로 `full_clean()` 호출 — 모델 유효성 검증이 항상 실행됨
- `pre_save()`: 서브클래스에서 override하여 save 전 전처리 (예: title.strip())
- `update_fields` 지정 시 `full_clean()` 건너뜀 (성능 최적화)
- 기본 ordering: `-created_at`
- **SoftDeleteMixin**: soft delete가 필요한 모델에 `SoftDeleteMixin`을 `BaseModel` 앞에 상속 — `class MyModel(SoftDeleteMixin, BaseModel)`
- **Cascade 정책**: `soft_delete_cascade` dict로 FK별 정책 설정. `SOFT_CASCADE`(부모 soft→자식 soft, 부모 restore→자식 restore), `SOFT_CASCADE_HARD_CHILDREN`(부모 soft→자식 hard delete), `HARD_CASCADE_SOFT_CHILDREN`(부모 hard→자식 soft+FK null)
- **Manager**: `objects`는 alive만 반환, `all_objects`는 삭제된 항목 포함 전체 반환
- **Bulk delete**: QuerySet.delete()는 cascade 미적용 (UPDATE만). cascade 필요 시 개별 instance.delete() 호출

<!-- MANUAL: -->
