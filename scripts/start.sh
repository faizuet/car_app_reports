#!/bin/bash
set -e

echo "Starting FastAPI web container..."
echo "Environment: ${ENV:-production}"

if [ "$ENV" = "development" ]; then
    # Development mode with reload and unbuffered output
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
else
    # Production mode with unbuffered output
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
fi

