<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-08 -->

# commands

## Purpose
커스텀 Django 관리 명령어. 리소스 스캐폴딩 생성기와 데이터베이스 시딩 명령어를 제공한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `generate_resource.py` | **generate_resource** — 리소스 스캐폴딩 생성기. 복수형 snake_case 이름으로 모델, 뷰, 시리얼라이저, 필터, URL, 테스트 파일 자동 생성. `--user-scoped`, `--fields`, `--model-name`, `--no-tests` 옵션 지원. `config/settings/base.py`와 `config/urls.py`에 자동 등록 |
| `seed.py` | **seed** — 데이터베이스 시딩 명령어 |

## For AI Agents

### Working In This Directory
- 새 명령어: `BaseCommand` 상속, `handle()` 메서드 구현
- 생성기 사용: `python manage.py generate_resource products --fields "name:CharField price:IntegerField" --user-scoped`
- 단축: `make generate name=products fields="name:CharField price:IntegerField"`
- 지원 필드 타입: CharField, TextField, IntegerField, BooleanField, DateTimeField, DateField, DecimalField, FloatField, IntegerChoices
- 생성기가 자동으로 apps/ + tests/ 디렉토리에 파일 생성, settings + urls 등록

### generate_resource 생성 파일
```
apps/{name}/
├── __init__.py, apps.py, models.py, views.py
├── serializers.py, filters.py, urls.py
└── migrations/__init__.py

tests/{name}/
├── __init__.py, test_models.py, test_api.py
```

<!-- MANUAL: -->
