#!/bin/bash
set -e

echo "Starting Celery beat..."

LOG_LEVEL=${LOG_LEVEL:-info}

celery -A car_tasks.celery_app beat --loglevel=$LOG_LEVEL

