<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-03-15 | Updated: 2026-03-15 -->

# snapshots

## Purpose
API 스키마 스냅샷 파일. OpenAPI 스키마 변경을 감지하여 의도하지 않은 API 변경을 방지한다.

## Key Files

| File | Description |
|------|-------------|
| `api_schema.json` | OpenAPI 스키마 스냅샷 — `make update-schema`로 갱신, `tests/core/test_schema_snapshot.py`에서 비교 검증 |

## For AI Agents

### Working In This Directory
- **이 파일을 직접 편집하지 마라.** API 변경 후 반드시 `make update-schema`로 자동 갱신하라.
- 스키마 스냅샷 테스트 실패 시: API가 의도적으로 변경되었다면 `make update-schema` 실행 후 커밋
- 스키마 비교 테스트: `tests/core/test_schema_snapshot.py`

<!-- MANUAL: -->
