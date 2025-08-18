#!/bin/bash
set -e

echo "Starting Celery worker..."
exec celery -A car_tasks.celery_app:celery worker --loglevel=info -P solo
