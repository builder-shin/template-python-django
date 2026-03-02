# Template Python Django

Python Django 5 기반 JSON:API 백엔드 템플릿 프로젝트입니다.

## 기술 스택

- **Python** 3.12
- **Django** 5.1
- **Django REST Framework** 3.15 - REST API 프레임워크
- **PostgreSQL** - 데이터베이스
- **Redis** - 캐시 및 Celery 브로커
- **Celery** - 백그라운드 작업 처리
- **djangorestframework-jsonapi** - JSON:API 스펙 준수
- **drf-spectacular** - OpenAPI/Swagger API 문서 자동 생성

## 필요 환경

- Python 3.12+
- PostgreSQL
- Redis (Celery / 캐시용)

## 빠른 시작

```bash
make setup    # 프로젝트 초기 설정 (uv, 의존성, DB, pre-commit)
make dev      # 개발 서버 실행 (http://localhost:4000)
```

## API 문서

개발 서버 실행 후 아래 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: `http://localhost:4000/api-docs/`
- **OpenAPI Schema**: `http://localhost:4000/api/schema/`

## Health Check

- `GET /health/live` - 서버 생존 확인
- `GET /health/ready` - 서버 준비 상태 확인 (DB + Cache 연결 포함)

## 개발 명령어

| 명령어 | 설명 |
|--------|------|
| `make help` | 사용 가능한 명령어 목록 표시 |
| `make setup` | 프로젝트 초기 설정 (uv, 의존성, DB, pre-commit) |
| `make dev` | 개발 서버 실행 (포트 4000, Celery eager mode) |
| `make server` | Docker Compose 전체 스택 실행 |
| `make shell` | Django 쉘 (모델 자동 import) |
| `make test` | 테스트 실행 |
| `make test-cov` | 커버리지 포함 테스트 실행 |
| `make lint` | 코드 린트 (Ruff) |
| `make format` | 코드 포맷팅 (Ruff fix + format) |
| `make migrate` | 마이그레이션 실행 |
| `make makemigrations` | 마이그레이션 파일 생성 |
| `make seed` | 개발용 샘플 데이터 생성 |
| `make generate` | 새 리소스 생성 (아래 참조) |
| `make clean` | 캐시, pyc, __pycache__ 정리 |
| `make worker` | Celery 워커 실행 (비동기 태스크 테스트용) |
| `make beat` | Celery Beat 스케줄러 실행 |
| `make dev-all` | 전체 개발 스택 실행 (web + celery worker + beat) |
| `make pre-commit` | 전체 파일에 pre-commit 실행 |
| `make docker-up` | Docker Compose 백그라운드 실행 |
| `make docker-down` | Docker Compose 중지 |

## 새 리소스 추가 (코드 생성기)

`generate_resource` 명령으로 새 API 리소스의 모든 파일을 자동 생성할 수 있습니다:

```bash
# 기본 사용법 (리소스명은 복수형 snake_case)
make generate name=products fields="name:CharField price:IntegerField status:IntegerChoices"

# user_id 자동 설정 (소유권 기반 접근 제어 포함)
python manage.py generate_resource order_items \
  --fields "name:CharField quantity:IntegerField" \
  --user-scoped
```

### 지원 필드 타입

| 타입 | Django 필드 | 기본 옵션 |
|------|------------|----------|
| `CharField` | `CharField` | `max_length=255` |
| `TextField` | `TextField` | `blank=True, default=""` |
| `IntegerField` | `IntegerField` | `default=0` |
| `BooleanField` | `BooleanField` | `default=False` |
| `DateTimeField` | `DateTimeField` | `null=True, blank=True` |
| `DateField` | `DateField` | `null=True, blank=True` |
| `DecimalField` | `DecimalField` | `max_digits=10, decimal_places=2` |
| `FloatField` | `FloatField` | `default=0.0` |
| `IntegerChoices` | `IntegerField` + `Status` class | `choices=Status.choices, default=0` |

### 생성되는 파일

```
apps/<name>/
├── __init__.py
├── apps.py              # AppConfig
├── models.py            # Model + QuerySet
├── views.py             # ViewSet (ApiViewSet)
├── serializers.py       # Serializer (HookableSerializerMixin)
├── filters.py           # django-filter FilterSet
├── urls.py              # URL 라우팅
└── migrations/
    └── __init__.py

tests/<name>/
├── __init__.py
├── test_models.py       # 모델 테스트
└── test_api.py          # API 테스트
```

생성 후 `config/settings/base.py`와 `config/urls.py`에 자동 등록됩니다.

> **참고**: v1은 스칼라 필드만 지원합니다. ForeignKey 등 관계 필드는 수동으로 추가하세요 (참고: `apps/comments/`).

## Docker

### 빌드

```bash
docker build -t template-python-django .
```

### 실행

```bash
docker run -p 4000:4000 --env-file .env template-python-django
```

### Docker Compose (전체 스택)

```bash
make server
# 또는
docker-compose up
# PostgreSQL, Redis, Web, Celery Worker, Celery Beat 모두 실행
```

## 디렉토리 구조

```
├── apps/
│   ├── core/                  # 핵심 인프라
│   │   ├── middleware/        # 미들웨어 (인증, 로깅, Allow2Ban)
│   │   ├── mixins/            # HookableSerializer, OwnedResource 등 공통 믹스인
│   │   ├── management/        # 커스텀 관리 명령어 (seed, generate_resource)
│   │   ├── authentication.py  # 인증 설정 (Django 내장 Session + Token)
│   │   ├── exceptions.py      # JSON:API 에러 핸들러
│   │   ├── filters.py         # AllowedIncludesFilter
│   │   ├── pagination.py      # JSON:API 페이지네이션
│   │   ├── permissions.py     # 권한 클래스
│   │   ├── serializers.py     # 베이스 시리얼라이저
│   │   ├── throttles.py       # 요청 제한
│   │   └── views.py           # API 베이스 뷰셋
│   ├── email_service/         # SendGrid 이메일 서비스
│   ├── members/               # 회원 리소스
│   ├── posts/                 # 게시글 리소스
│   └── comments/              # 댓글 리소스
├── config/
│   ├── settings/              # 환경별 설정
│   │   ├── base.py            # 공통 설정
│   │   ├── development.py     # 개발 환경
│   │   ├── production.py      # 프로덕션 환경
│   │   └── test.py            # 테스트 환경
│   ├── celery.py              # Celery 설정
│   ├── asgi.py               # ASGI 애플리케이션
│   ├── urls.py                # 루트 URL 설정
│   └── wsgi.py                # WSGI 애플리케이션
├── tests/                     # pytest 테스트
│   ├── factories.py           # factory-boy 팩토리 정의
│   └── conftest.py            # 테스트 픽스처
├── scripts/
│   └── setup.sh               # 프로젝트 초기 설정 스크립트
├── pyproject.toml             # 의존성 및 도구 설정 (uv)
├── uv.lock                    # uv 락파일 (재현 가능한 빌드)
├── .github/
│   └── workflows/ci.yml       # GitHub Actions CI
├── Dockerfile                 # Docker 빌드 설정
├── docker-compose.yml         # Docker Compose 설정
├── Makefile                   # 개발 명령어 통합
├── Procfile.dev               # 멀티 프로세스 개발 실행
├── gunicorn.conf.py           # Gunicorn 서버 설정
├── manage.py                  # Django 관리 스크립트
├── .pre-commit-config.yaml    # pre-commit 훅 설정
└── .env.example               # 환경 변수 템플릿
```

## 환경 변수

환경 변수 목록은 `.env.example` 파일을 참고하세요.

## 주요 패턴

### JSON:API

- `?include=relation` - 관계 포함 (자동 eager loading)
- `?filter[attr]=value` / `?filter[attr.lookup]=value` - django-filter 필터링 (exact, icontains, gt, lt 등)
- `?page[number]=1&page[size]=10` - 페이지네이션

### 인증

Django 내장 인증 시스템을 사용합니다 (SessionAuthentication + TokenAuthentication).

```python
# views.py에서 권한 클래스 설정
permission_classes = [IsAuthenticated]     # 인증 필수
```

### ApiViewSet 라이프사이클 훅

`ApiViewSet`은 CRUD + upsert 기능과 라이프사이클 훅을 내장하고 있습니다. Serializer에는 `HookableSerializerMixin`을 함께 사용해야 훅이 정상 동작합니다:

```python
class MyViewSet(ApiViewSet):
    serializer_class = MySerializer
    filterset_class = MyFilterSet

    def create_after_init(self, instance):
        instance.user_id = self.request.user.id

    def create_after_save(self, instance, success):
        if success:
            send_notification.delay(instance.id)
```

소유권 기반 접근 제어가 필요하면 라이프사이클 훅을 직접 구현합니다:

```python
class MyViewSet(ApiViewSet):
    serializer_class = MySerializer

    def _check_ownership(self, instance, action_label: str) -> None:
        if str(instance.user_id) != str(self.request.user.id):
            raise JsonApiError("Forbidden", f"본인의 리소스만 {action_label}할 수 있습니다.", 403)

    def create_after_init(self, instance) -> None:
        instance.user_id = str(self.request.user.id)

    def update_after_init(self, instance) -> None:
        self._check_ownership(instance, "수정")

    def destroy_after_init(self, instance) -> None:
        self._check_ownership(instance, "삭제")
```

## 테스트

```bash
# 전체 테스트
make test

# 커버리지 포함
make test-cov

# 특정 파일 테스트
pytest tests/posts/test_api.py

# 특정 테스트
pytest tests/posts/test_api.py::TestPostsAPI::test_list_posts
```

### 테스트 팩토리

`tests/factories.py`에 factory-boy 팩토리가 정의되어 있습니다:

```python
from tests.factories import PostFactory, MemberFactory, CommentFactory

post = PostFactory()  # 기본 Post 생성
post = PostFactory(title="커스텀 제목", status=1)  # 커스텀 속성
posts = PostFactory.create_batch(5)  # 5개 일괄 생성
```

## 코드 품질

### Pre-commit 훅

커밋 시 자동으로 Ruff (lint + format)가 실행됩니다:

```bash
# 수동 실행
make pre-commit

# 설치 (make setup에서 자동 실행)
pre-commit install
```

### 린트 & 포맷팅

```bash
make lint     # Ruff 린트
make format   # Ruff fix + format
```

## CI/CD

GitHub Actions가 push/PR 시 자동으로 실행됩니다:

- **Lint**: Ruff check + format 검증
- **Test**: PostgreSQL 16 + Redis 7 환경에서 pytest 실행 (커버리지 포함)

워크플로우 설정: `.github/workflows/ci.yml`

## 주의사항

- 이 템플릿은 기본적인 설정을 포함하고 있으며, 실제 사용 시에는 프로젝트에 맞게 설정을 수정해야 합니다.
- 환경 변수 설정은 `.env` 파일을 사용하여 관리합니다.
- `generate_resource`로 생성된 코드는 스칼라 필드만 지원합니다. 관계 필드(ForeignKey 등)는 `apps/comments/`를 참고하여 수동으로 추가하세요.
