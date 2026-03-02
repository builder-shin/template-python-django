<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-02 -->

# apps

## Purpose
Django 애플리케이션 모듈 모음. 각 앱은 독립적인 도메인을 담당하며, `core` 앱이 공통 인프라(ApiViewSet, 미들웨어, 인증 등)를 제공한다.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `core/` | 공통 인프라 — ApiViewSet, 예외 처리, 필터, 미들웨어, 믹스인, 유틸리티 (see `core/AGENTS.md`) |
| `members/` | 회원 프로필 관리 — Member 모델, /me 엔드포인트 (see `members/AGENTS.md`) |
| `posts/` | 게시글 관리 — Post 모델, 발행/아카이브 워크플로우, upsert (see `posts/AGENTS.md`) |
| `comments/` | 댓글 관리 — Comment 모델, 대댓글(self-referential), post 관계 (see `comments/AGENTS.md`) |
| `email_service/` | 이메일 발송 — SendGrid 템플릿 이메일 서비스 (see `email_service/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 새 앱 추가 시 `make generate name=앱이름 fields="필드:타입"` 사용
- 모든 앱의 ViewSet은 `apps.core.views.ApiViewSet`을 상속
- 모든 Serializer는 `HookableSerializerMixin`을 첫 번째 부모로 상속
- CoC 패턴: serializer_class, filterset_class 명시 불필요 (자동 추론)
- user_id 기반 소유권이 필요한 앱은 `UserScopedMixin` 사용
- 앱 등록: `config/settings/base.py` INSTALLED_APPS + `config/urls.py` urlpatterns

### App Structure Convention
각 앱의 표준 파일 구조:
```
apps/{name}/
├── __init__.py
├── apps.py          # AppConfig
├── models.py        # 모델 + QuerySet
├── views.py         # ViewSet (ApiViewSet 상속)
├── serializers.py   # Serializer (HookableSerializerMixin 상속)
├── filters.py       # FilterSet (django_filters)
├── urls.py          # DefaultRouter + urlpatterns
└── migrations/      # Django 마이그레이션
```

### Common Patterns
- 각 앱은 독립적 도메인 — 앱 간 참조는 ForeignKey 또는 user_id(문자열)로
- `user_id`는 CharField (Django User의 ID를 문자열로 저장)
- 모든 모델에 `created_at`, `updated_at` 자동 필드

<!-- MANUAL: -->
