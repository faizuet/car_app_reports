#!/bin/bash
set -e

echo "Starting FastAPI web container..."
echo "Environment: ${ENV:-production}"

echo "Running database migrations..."
alembic upgrade head

if [ "$ENV" = "development" ]; then
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
else
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
fi
