<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-06 -->

# email_service

## Purpose
이메일 발송 서비스. SendGrid API를 통한 템플릿 기반 이메일 발송 (단건 + 배치)을 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `sendgrid_service.py` | **SendGridEmailService** — `send_template_email` (단건), `send_batch_template_emails` (최대 1000건/API 호출, Personalization 기반 배치). settings.SENDGRID_API_KEY 미설정 시 graceful skip. 이메일 주소 로깅 시 자동 마스킹 |
| `apps.py` | EmailServiceConfig |

## For AI Agents

### Working In This Directory
- SendGrid 설정 필요: `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`, `SENDGRID_FROM_NAME` (settings/환경변수)
- 배치 발송: MAX_BATCH_SIZE=1000, 초과 시 자동 청크 분할
- `enabled()` 메서드로 설정 유무 체크 후 graceful 처리
- Celery 태스크에서 호출하여 비동기 발송 권장

<!-- MANUAL: -->
