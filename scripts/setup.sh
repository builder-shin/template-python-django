#!/usr/bin/env bash
set -e

echo "=== 프로젝트 설정 시작 ==="

# 1. uv 설치 확인
if ! command -v uv &> /dev/null; then
    echo ">>> uv 설치..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "    uv가 설치되었습니다. 터미널을 재시작하거나 PATH를 갱신하세요."
fi

# 2. 의존성 설치 (가상환경 자동 생성)
echo ">>> 의존성 설치..."
uv sync --group dev --group test

# 3. .env 파일 복사 (없으면)
if [ ! -f ".env" ]; then
    echo ">>> .env 파일 생성..."
    cp .env.example .env
    echo "    .env 파일을 열어 값을 확인하세요."
fi

# 4. 마이그레이션
echo ">>> 데이터베이스 마이그레이션..."
uv run python manage.py migrate

# 5. pre-commit 설치
if command -v pre-commit &> /dev/null || uv run which pre-commit &> /dev/null; then
    echo ">>> pre-commit 훅 설치..."
    uv run pre-commit install
fi

echo ""
echo "=== 설정 완료! ==="
echo "  개발 서버: make dev"
echo "  테스트:    make test"
echo "  도움말:    make help"
