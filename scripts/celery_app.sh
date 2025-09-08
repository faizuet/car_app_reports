#!/bin/bash
set -e

echo "Starting Celery worker..."

LOG_LEVEL=${LOG_LEVEL:-info}

CONCURRENCY=${CONCURRENCY:-1}

celery -A car_tasks.celery_app worker --loglevel=$LOG_LEVEL --concurrency=$CONCURRENCY

