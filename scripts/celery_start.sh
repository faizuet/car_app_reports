#!/bin/sh

celery -A tasks.celery_worker.celery beat --loglevel=info &
celery -A tasks.celery_worker.celery worker --loglevel=info
