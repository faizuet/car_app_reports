#!/bin/bash
set -e

echo "Starting Celery beat..."
exec celery -A car_tasks.celery_app:celery beat --loglevel=info
