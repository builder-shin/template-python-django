<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-12 -->

# tests/core

## Purpose
Core 인프라 테스트. CoC 자동 추론, CrudActions 라이프사이클 훅, JWT 인증을 검증한다.

## Key Files

| File | Description |
|------|-------------|
| `test_coc_inference.py` | **CoC 추론 테스트** — serializer_class, included_serializers 자동 추론, filterset_class CoC 자동 추론(allowed_filters dict에서 동적 생성, TestFiltersetClassCoC), 캐싱, 에러 케이스 |
| `test_crud_actions.py` | **CrudActions 테스트** — create/update/destroy 라이프사이클 훅 호출 순서, HookableSerializerMixin 동작, M2M 필드 처리 |
| `test_auth.py` | **JWT 인증 테스트** — login, refresh (토큰 로테이션), logout, logout-all, 토큰 만료/무효화 |
| `test_health.py` | **Health Check 테스트** — `/health/live`, `/health/ready` 엔드포인트, DB/Cache 장애 시나리오 |
| `test_hookable_serializer.py` | **HookableSerializerMixin 테스트** — create/update 훅 호출, M2M 필드 분리 처리 검증 |
| `test_make_urlpatterns.py` | **make_urlpatterns 테스트** — basename 자동 추론, only 파라미터, URL 패턴 생성 |
| `test_permissions.py` | **권한 테스트** — IsOwnerOrReadOnly 퍼미션 검증 |
| `test_schema_snapshot.py` | **API 스키마 스냅샷 테스트** — OpenAPI 스키마 변경 감지 (tests/snapshots/api_schema.json 비교) |
| `test_tasks.py` | **Celery 태스크 테스트** — send_notification 태스크 실행, 재시도, 에러 처리 |

## For AI Agents

### Working In This Directory
- CoC 테스트: Mock ViewSet/Serializer로 자동 추론 로직 검증
- CrudActions 테스트: 훅 호출 여부 및 순서 검증
- Auth 테스트: JWT 토큰 생성/검증/무효화 흐름 검증
- `apps/core/views.py` 변경 시 반드시 이 테스트 실행

<!-- MANUAL: -->
