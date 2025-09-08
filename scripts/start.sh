#!/bin/bash
set -e

echo "Starting FastAPI..."

if [ "$ENV" = "development" ]; then
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
