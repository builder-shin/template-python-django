<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-28 | Updated: 2026-02-28 -->

# commands

## Purpose
Django management 커맨드 구현. `python manage.py <command>` 형태로 실행되는 커스텀 커맨드를 포함한다.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 패키지 초기화 |
| `setup_fdw.py` | `setup_fdw` — PostgreSQL Foreign Data Wrapper 설정 (인증 서비스 DB 크로스 접근) |

## For AI Agents

### Working In This Directory
- `setup_fdw` 커맨드: `--setup` (기본), `--teardown`, `--test`, `--refresh` 옵션
- FDW 대상 테이블: `auth.users`, `auth.user_consents`, `auth.workspaces`, `auth.workspace_members`
- 환경변수: `AUTH_DB_HOST`, `AUTH_DB_PORT`, `AUTH_DB_NAME`, `AUTH_DB_USER`, `AUTH_DB_PASSWORD`
- 새 커맨드 추가 시 이 디렉토리에 `BaseCommand` 상속 클래스 파일 생성

### Usage
```bash
python manage.py setup_fdw          # FDW 설정
python manage.py setup_fdw --test   # 연결 테스트
python manage.py setup_fdw --teardown  # FDW 제거
python manage.py setup_fdw --refresh   # 재설정
```

<!-- MANUAL: -->
