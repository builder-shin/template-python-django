<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-08 -->

# apps

## Purpose
Django 애플리케이션 모듈 모음. `core` 앱이 공통 인프라(ApiViewSet, JWT 인증, 미들웨어 등)를 제공하고, 나머지는 도메인 리소스 앱.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `core/` | 공통 인프라 — ApiViewSet, JWT 인증, 예외 처리, 필터, 미들웨어, 믹스인, 유틸리티 (see `core/AGENTS.md`) |
| `users/` | 사용자 모델 및 API — AbstractUser 확장, /me 엔드포인트 (see `users/AGENTS.md`) |
| `posts/` | 게시글 관리 — Post 모델, 발행/아카이브 워크플로우, upsert (see `posts/AGENTS.md`) |
| `comments/` | 댓글 관리 — Comment 모델, 대댓글(self-referential), post 관계 (see `comments/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- 새 앱 추가 시 `make generate name=앱이름 fields="필드:타입"` 사용
- 모든 앱의 ViewSet은 `apps.core.views.ApiViewSet`을 상속
- 모든 Serializer는 `HookableSerializerMixin`을 첫 번째 부모로 상속
- CoC 패턴: serializer_class, filterset_class 명시 불필요 (자동 추론)
- 앱 등록: `config/settings/base.py` INSTALLED_APPS + `config/urls.py` urlpatterns

### App Structure Convention
각 앱의 표준 파일 구조:
```
apps/{name}/
├── __init__.py
├── apps.py          # AppConfig
├── models.py        # 모델 (BaseModel 상속)
├── views.py         # ViewSet (ApiViewSet 상속)
├── serializers.py   # Serializer (HookableSerializerMixin 상속)
├── filters.py       # FilterSet (django_filters)
├── urls.py          # make_urlpatterns() 사용
└── migrations/      # Django 마이그레이션
```

<!-- MANUAL: -->
