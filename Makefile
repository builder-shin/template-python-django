.PHONY: help setup dev server shell test test-cov test-cov-html lint format migrate makemigrations seed generate update-schema clean worker beat dev-all pre-commit docker-up docker-down

.DEFAULT_GOAL := help

help: ## 사용 가능한 명령어 목록 표시
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## 프로젝트 초기 설정 (uv, 의존성, DB, pre-commit)
	@bash scripts/setup.sh

dev: ## 개발 서버 실행 (포트 4000, Celery eager mode)
	uv run python manage.py runserver 0.0.0.0:4000

server: ## Docker Compose 전체 스택 실행
	docker compose up

shell: ## Django 쉘 (모델 자동 import)
	uv run python manage.py shell_plus --ipython

test: ## 테스트 실행
	uv run pytest

test-cov: ## 커버리지 포함 테스트 실행
	uv run pytest --cov=apps --cov-report=term-missing

test-cov-html: ## 커버리지 HTML 리포트 생성 (htmlcov/)
	uv run pytest --cov=apps --cov-report=term-missing --cov-report=html

lint: ## 코드 린트 (Ruff)
	uv run ruff check .

format: ## 코드 포맷팅 (Ruff fix + format)
	uv run ruff check --fix .
	uv run ruff format .

migrate: ## 마이그레이션 실행
	uv run python manage.py migrate

makemigrations: ## 마이그레이션 파일 생성
	uv run python manage.py makemigrations

seed: ## 개발용 샘플 데이터 생성
	uv run python manage.py seed

generate: ## 새 리소스 생성 (예: make generate name=products fields="title:CharField")
ifndef name
	$(error name 인자가 필요합니다. 예: make generate name=products fields="title:CharField")
endif
	uv run python manage.py generate_resource $(name) $(if $(fields),--fields $(fields),)

update-schema: ## API 스키마 스냅샷 갱신
	mkdir -p tests/snapshots
	DJANGO_SETTINGS_MODULE=config.settings.test uv run python manage.py spectacular --format openapi-json | uv run python -c "import sys,json; print(json.dumps(json.load(sys.stdin), sort_keys=True, indent=2))" > tests/snapshots/api_schema.json

clean: ## 캐시, pyc, __pycache__ 정리
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

worker: ## Celery 워커 실행 (비동기 태스크 테스트용)
	uv run celery -A config worker -l info

beat: ## Celery Beat 스케줄러 실행
	uv run celery -A config beat -l info

dev-all: ## 전체 개발 스택 실행 (web + celery worker + beat)
	CELERY_TASK_ALWAYS_EAGER= uv run honcho start -f Procfile.dev

pre-commit: ## 전체 파일에 pre-commit 실행
	uv run pre-commit run --all-files

docker-up: ## Docker Compose 백그라운드 실행
	docker compose up -d

docker-down: ## Docker Compose 중지
	docker compose down
