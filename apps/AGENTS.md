<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# apps

## Purpose
Django 애플리케이션 모듈의 컨테이너 디렉토리. 각 앱은 독립적인 도메인을 담당하며, `core` 앱이 공통 인프라를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `core/` | 공통 인프라 — 인증, 권한, 예외처리, 필터, 미들웨어, CRUD 믹스인 (see `core/AGENTS.md`) |
| `auth_service/` | 외부 인증 서비스 연동 클라이언트 및 AuthUser 모델 (see `auth_service/AGENTS.md`) |
| `posts/` | 게시글 CRUD API (see `posts/AGENTS.md`) |
| `comments/` | 댓글 CRUD API, 대댓글 지원 (see `comments/AGENTS.md`) |
| `members/` | 회원 프로필 CRUD API (see `members/AGENTS.md`) |
| `email_service/` | SendGrid 이메일 발송 서비스 (see `email_service/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 새 앱 추가 시: `apps/` 하위에 디렉토리 생성 후 `config/settings/base.py`의 `INSTALLED_APPS`에 등록
- 모든 앱은 `core` 앱의 공통 모듈을 상속/활용
- ViewSet은 `CrudActionsMixin + ApiViewSet` 패턴, Serializer는 `HookableSerializerMixin` 포함 필수
- URL은 `config/urls.py`에서 `api/v1/` 접두사로 include

### Common Patterns
- 각 도메인 앱 구조: `models.py`, `serializers.py`, `views.py`, `filters.py`, `urls.py`, `migrations/`
- `user_id`는 CharField로 외부 인증 서비스의 ID를 참조 (FK 아님)
- 모든 모델에 `created_at`/`updated_at` 타임스탬프

<!-- MANUAL: -->
