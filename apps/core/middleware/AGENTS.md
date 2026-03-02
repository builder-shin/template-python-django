<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# middleware

## Purpose
Django HTTP 미들웨어. 요청 처리 파이프라인에서 IP 차단 등의 횡단 관심사를 처리한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `allow2ban.py` | **Allow2BanMiddleware** — settings.BLOCKED_IPS에 등록된 IP 차단 (403 응답) |

## For AI Agents

### Working In This Directory
- 미들웨어 등록: `config/settings/base.py` MIDDLEWARE 리스트에 추가
- 순서 중요: SecurityMiddleware 이후, CommonMiddleware 이전 권장
- IP 추출: `apps.core.utils.get_client_ip` (django-ipware 기반) 사용

<!-- MANUAL: -->
