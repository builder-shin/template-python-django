<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# apps

## Purpose
Django 애플리케이션 모듈 컨테이너. 도메인(members, posts, comments), 인프라(core, email_service)로 구분된 5개 앱을 포함.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `core/` | 공통 기반 — 인증, 예외, 필터, 미들웨어, Mixin, 관리 명령어 (see `core/AGENTS.md`) |
| `email_service/` | SendGrid 이메일 발송 서비스 (see `email_service/AGENTS.md`) |
| `members/` | 회원 프로필 도메인 (see `members/AGENTS.md`) |
| `posts/` | 게시글 도메인 (see `posts/AGENTS.md`) |
| `comments/` | 댓글 도메인 (see `comments/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 새 앱 생성: `make generate name=<복수형> fields="<필드 정의>"` 사용
- 앱 구조 패턴: `models.py`, `views.py`, `serializers.py`, `filters.py`, `urls.py`, `apps.py`
- 모든 ViewSet은 `ApiViewSet` 상속 (CRUD 라이프사이클 훅 내장)
- 소유권 검증이 필요한 ViewSet은 `OwnedResourceMixin` 추가 상속
- 모든 Serializer는 `HookableSerializerMixin + serializers.ModelSerializer` 상속
- 필터는 표준 `django_filters.FilterSet` 클래스 사용

### Common Patterns
- 각 앱은 독립적 도메인 — 앱 간 참조는 ForeignKey 또는 user_id(문자열)로
- `user_id`는 CharField (Django User의 ID를 문자열로 저장)
- 모든 모델에 `created_at`, `updated_at` 자동 필드

<!-- MANUAL: -->
