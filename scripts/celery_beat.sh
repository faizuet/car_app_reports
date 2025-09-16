#!/bin/bash
set -e

# Default log level
LOG_LEVEL=${CELERY_LOG_LEVEL:-info}

# Start Celery beat
celery -A car_tasks.celery_app beat --loglevel="$LOG_LEVEL"

