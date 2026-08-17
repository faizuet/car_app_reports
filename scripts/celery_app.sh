#!/bin/bash
set -e

echo "Starting Celery worker..."

# Use solo pool on Windows-friendly setups; concurrency=1 for Docker/Linux too
celery -A car_tasks.celery_app worker --loglevel=info --pool=solo
