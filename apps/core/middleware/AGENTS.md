<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# middleware

## Purpose
커스텀 Django 미들웨어. IP 자동 차단(Allow2Ban) 제공. 구조화 로깅은 django-structlog 패키지로 대체됨.

## Key Files

| File | Description |
|------|-------------|
| `allow2ban.py` | `Allow2BanMiddleware` — 의심 경로 스캔 공격 IP 자동 차단 (Redis 캐시, 20회/60초 → 1시간 ban) |

## For AI Agents

### Working In This Directory
- 미들웨어 순서 (base.py): CORS → Security → CSP → **Allow2Ban** → Common → Session → Auth → django-structlog
- Allow2Ban 의심 패턴: `/etc/passwd`, `wp-admin`, `wp-login`, `.env`, `phpinfo`, `phpmyadmin`
- 클라이언트 IP: `apps.core.utils.get_client_ip()` 사용 (django-ipware 기반)
- 이전에 존재하던 `current_user.py`, `structured_logging.py`는 삭제됨 — django-structlog 패키지로 대체

### Testing Requirements
- Allow2Ban: Redis 캐시 의존 — 테스트 시 LocMemCache로 대체됨

<!-- MANUAL: -->
