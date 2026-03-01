<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-03-01 -->

# commands

## Purpose
Django 커스텀 관리 명령어. 코드 생성, 시드 데이터, FDW 설정 제공.

## Key Files

| File | Description |
|------|-------------|
| `generate_resource.py` | 리소스 스캐폴드 생성기 — 모델/뷰/시리얼라이저/필터/URL/테스트를 한번에 생성하고 settings/urls에 자동 등록 |
| `seed.py` | 개발용 샘플 데이터 생성 — Member 10개, Post 20개, Comment 30개 (factory-boy 사용) |
| `setup_fdw.py` | PostgreSQL Foreign Data Wrapper 설정 — 인증 서비스 DB 크로스 액세스 (users, workspaces 등) |

## For AI Agents

### Working In This Directory
- `generate_resource` 사용법: `python manage.py generate_resource <복수형_snake> --fields "name:CharField content:TextField" --user-scoped`
- 지원 필드 타입: CharField, TextField, IntegerField, BooleanField, DateTimeField, DateField, DecimalField, FloatField, IntegerChoices
- `--user-scoped`: user_id 필드 및 소유권 검증 훅 자동 추가
- `--model-name`: inflect 단수화 결과 오버라이드
- `seed` 명령어: `--flush` 옵션으로 기존 데이터 삭제 후 생성
- `setup_fdw`: 인증 서비스 PostgreSQL DB에 대한 FDW 설정 (`--teardown`, `--test`, `--refresh`)

### Testing Requirements
- generate_resource는 통합 테스트로 검증 (실제 파일 생성 확인)
- seed는 factories.py 의존

<!-- MANUAL: -->
