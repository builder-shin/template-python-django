<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# auth_service

## Purpose
AuthServiceClient 테스트. 인증 성공/실패, 서킷 브레이커, 캐싱, 재시도 로직 검증.

## Key Files

| File | Description |
|------|-------------|
| `test_client.py` | AuthServiceClient 테스트 — verify_session, 서킷 브레이커, 캐시, 재시도, 에러 처리 |

## For AI Agents

### Working In This Directory
- respx로 외부 인증 서비스 API 모킹
- 서킷 브레이커 테스트 후 `AuthServiceClient.reset_circuit()` 호출
- httpx.Client 테스트 후 `AuthServiceClient.reset_client()` 호출

<!-- MANUAL: -->
