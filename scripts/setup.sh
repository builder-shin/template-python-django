#!/usr/bin/env bash
set -e

echo "=== 프로젝트 설정 시작 ==="

# 1. Python 가상환경 생성 (없으면)
if [ ! -d ".venv" ]; then
    echo ">>> 가상환경 생성..."
    python3 -m venv .venv
fi

# 2. 가상환경 활성화
source .venv/bin/activate

# 3. 의존성 설치
echo ">>> 의존성 설치..."
pip install -q -r requirements/dev.txt -r requirements/test.txt

# 4. .env 파일 복사 (없으면)
if [ ! -f ".env" ]; then
    echo ">>> .env 파일 생성..."
    cp .env.example .env
    echo "    .env 파일을 열어 값을 확인하세요."
fi

# 5. 마이그레이션
echo ">>> 데이터베이스 마이그레이션..."
python manage.py migrate

# 6. pre-commit 설치
if command -v pre-commit &> /dev/null; then
    echo ">>> pre-commit 훅 설치..."
    pre-commit install
fi

echo ""
echo "=== 설정 완료! ==="
echo "  개발 서버: make dev"
echo "  테스트:    make test"
echo "  도움말:    make help"
