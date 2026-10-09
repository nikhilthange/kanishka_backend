#!/usr/bin/env bash
# Convenience runner for Linux / macOS / WSL
set -e

CMD=${1:-start}

case "$CMD" in
    test)
        echo "Running pytest test suite..."
        pytest -v
        ;;
    seed)
        echo "Running database seeder..."
        python seed.py
        ;;
    migrate)
        echo "Running Alembic migrations..."
        alembic upgrade head
        ;;
    start)
        echo "Starting FastAPI server at http://127.0.0.1:8000 (Docs at /docs)..."
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    *)
        echo "Usage: ./run.sh [test|seed|migrate|start]"
        exit 1
        ;;
esac
