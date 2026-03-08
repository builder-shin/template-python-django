<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-06 | Updated: 2026-03-08 -->

# models

## Purpose
공통 베이스 모델과 QuerySet. 모든 도메인 모델이 상속하는 추상 기본 클래스를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | `BaseModel`, `BaseQuerySet` 내보내기 |
| `base.py` | **BaseModel** — 추상 모델. `created_at`(auto_now_add), `updated_at`(auto_now). `save()` 시 `pre_save()` 호출 후 `full_clean()` 자동 실행 (update_fields 없을 때). **BaseQuerySet** — 도메인 QuerySet의 공통 메서드 제공 |

## For AI Agents

### Working In This Directory
- 모든 도메인 모델은 `BaseModel`을 상속해야 함
- `save()` 시 자동으로 `full_clean()` 호출 — 모델 유효성 검증이 항상 실행됨
- `pre_save()`: 서브클래스에서 override하여 save 전 전처리 (예: title.strip())
- `update_fields` 지정 시 `full_clean()` 건너뜀 (성능 최적화)
- 기본 ordering: `-created_at`

<!-- MANUAL: -->
