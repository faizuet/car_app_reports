#!/bin/bash
set -e

echo "Starting Celery worker..."

celery -A car_tasks.celery_app worker --loglevel=info --concurrency=1

