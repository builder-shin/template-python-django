<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# email_service

## Purpose
SendGrid 기반 이메일 발송 서비스. 템플릿 이메일 개별/배치 발송 기능을 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `apps.py` | Django 앱 설정 (`EmailServiceConfig`) |
| `sendgrid_service.py` | `SendGridEmailService` — 템플릿 이메일 발송, 배치 발송 (max 1000/call) |

## For AI Agents

### Working In This Directory
- SendGrid 미설정 시 graceful skip (warning 로그만 출력)
- 설정 필요: `settings.SENDGRID_API_KEY`, `settings.SENDGRID_FROM_EMAIL`
- 배치 발송은 1000건씩 Personalization으로 분할
- `sendgrid` 패키지는 함수 내 lazy import (미설치 시 에러 방지)

### Testing Requirements
- SendGrid API를 mock하여 테스트
- `enabled()` 메서드로 설정 유무 확인 후 분기

## Dependencies

### External
- `sendgrid` — SendGrid Python SDK

<!-- MANUAL: -->
