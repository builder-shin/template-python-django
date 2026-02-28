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

## 필요 환경

- Python 3.12+
- PostgreSQL
- Redis (Celery / 캐시용)

## 설정 및 실행

### 1. 가상환경 생성 및 의존성 설치

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 값을 채워넣으세요
```

### 3. 데이터베이스 설정

```bash
python manage.py migrate
```

### 4. 서버 실행

```bash
python manage.py runserver 0.0.0.0:4000
# http://localhost:4000 에서 실행됩니다
```

## 개발 명령어

| 명령어 | 설명 |
|--------|------|
| `python manage.py runserver 0.0.0.0:4000` | 개발 서버 실행 (포트 4000) |
| `python manage.py shell` | Django 쉘 |
| `pytest` | 테스트 실행 |
| `ruff check .` | 코드 린트 |
| `black .` | 코드 포맷팅 |
| `python manage.py migrate` | 마이그레이션 실행 |
| `python manage.py migrate <app> <migration>` | 특정 마이그레이션으로 롤백 |
| `python manage.py flush` | 데이터베이스 초기화 |
| `celery -A config worker -l info` | Celery 워커 실행 |
| `celery -A config beat -l info` | Celery Beat 스케줄러 실행 |
| `python manage.py setup_fdw` | FDW 설정 (Auth DB 연동) |

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
docker-compose up
# PostgreSQL, Redis, Web, Celery Worker, Celery Beat 모두 실행
```

## 디렉토리 구조

```
├── apps/
│   ├── core/                  # 핵심 인프라
│   │   ├── middleware/        # 미들웨어 (인증, 로깅)
│   │   ├── mixins/            # CrudActions 등 공통 믹스인
│   │   ├── management/        # 커스텀 관리 명령어 (FDW)
│   │   ├── authentication.py  # 쿠키 세션 인증
│   │   ├── exceptions.py      # JSON:API 에러 핸들러
│   │   ├── filters.py         # Ransack 스타일 필터
│   │   ├── pagination.py      # JSON:API 페이지네이션
│   │   ├── permissions.py     # 권한 클래스
│   │   ├── serializers.py     # 베이스 시리얼라이저
│   │   ├── throttles.py       # 요청 제한
│   │   └── views.py           # API 베이스 뷰셋
│   ├── auth_service/          # 외부 인증 서비스 연동
│   ├── email_service/         # SendGrid 이메일 서비스
│   └── examples/              # 예제 리소스 (참고용)
│       ├── models.py          # Example 모델
│       ├── serializers.py     # Example 시리얼라이저
│       ├── views.py           # Example 뷰셋
│       ├── filters.py         # Example 필터
│       └── urls.py            # Example URL 라우팅
├── config/
│   ├── settings/              # 환경별 설정
│   │   ├── base.py            # 공통 설정
│   │   ├── development.py     # 개발 환경
│   │   ├── production.py      # 프로덕션 환경
│   │   └── test.py            # 테스트 환경
│   ├── celery.py              # Celery 설정
│   ├── urls.py                # 루트 URL 설정
│   └── wsgi.py                # WSGI 애플리케이션
├── tests/                     # pytest 테스트
├── requirements/              # pip 의존성
│   ├── base.txt               # 프로덕션 의존성
│   ├── dev.txt                # 개발 의존성
│   └── test.txt               # 테스트 의존성
├── Dockerfile                 # Docker 빌드 설정
├── docker-compose.yml         # Docker Compose 설정
├── gunicorn.conf.py           # Gunicorn 서버 설정
├── pyproject.toml             # Python 프로젝트 메타데이터
├── manage.py                  # Django 관리 스크립트
└── .env.example               # 환경 변수 템플릿
```

## 환경 변수

환경 변수 목록은 `.env.example` 파일을 참고하세요.

## 주요 패턴

### JSON:API

- `?include=relation` - 관계 포함 (자동 eager loading)
- `?filter[attr_predicate]=value` - Ransack 스타일 필터링 (eq, cont, gt, lt 등)
- `?page[number]=1&page[size]=10` - 페이지네이션

### 인증

쿠키 기반 인증으로 외부 Auth 서비스와 연동합니다.

```python
# views.py에서 권한 클래스 설정
permission_classes = [IsAuthenticated]     # 인증 필수
permission_classes = [IsEnterprise]        # 기업회원만
permission_classes = [IsPersonal]          # 개인회원만
```

### CrudActions 믹스인

`CrudActionsMixin`은 CRUD + upsert 기능과 라이프사이클 훅을 제공합니다:

```python
class MyViewSet(CrudActionsMixin, ApiViewSet):
    model_class = MyModel
    serializer_class = MySerializer

    def create_after_init(self, instance):
        instance.user_id = self.request.user.id

    def create_after_save(self, instance, success):
        if success:
            send_notification.delay(instance.id)
```

## 테스트

```bash
# 전체 테스트
pytest

# 특정 파일 테스트
pytest tests/examples/test_api.py

# 특정 테스트
pytest tests/examples/test_api.py::TestExamplesAPI::test_list_examples

# 커버리지 포함
pytest --cov=apps
```

## 주의사항

- 이 템플릿은 기본적인 설정을 포함하고 있으며, 실제 사용 시에는 프로젝트에 맞게 설정을 수정해야 합니다.
- 환경 변수 설정은 `.env` 파일을 사용하여 관리합니다.
- `apps/examples/`는 참고용 예제입니다. 실제 프로젝트에서는 이를 기반으로 새 앱을 생성하세요.
