<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# email_service

## Purpose
SendGrid 기반 이메일 발송 서비스. 템플릿 이메일 단건/배치 발송 지원.

## Key Files

| File | Description |
|------|-------------|
| `sendgrid_service.py` | `SendGridEmailService` — 단건 `send_template_email()` + 배치 `send_batch_template_emails()` (최대 1000건/API 호출) |
| `apps.py` | Django AppConfig |

## For AI Agents

### Working In This Directory
- `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` 환경변수 필수
- `enabled()` 체크로 미설정 시 graceful skip
- 배치 발송: 1000건 단위 Personalization 분할
- 응답: `{ "success": bool, "status_code": int }` (단건), `{ "success": bool, "total": int, "sent": int, "failed": int }` (배치)

### Testing Requirements
- SendGrid 미설정 시 자동 스킵 로직 확인
- Mock 사용하여 외부 API 호출 차단

<!-- MANUAL: -->
