from celery import Celery
from datetime import timedelta
import os
from app import create_app

os.environ.setdefault('FLASK_APP', 'run.py')

flask_app = create_app()

celery = Celery(
    'car_app_reports',
    broker=os.getenv("CELERY_BROKER_URL", 'redis://localhost:6379/0'),
    backend=os.getenv("CELERY_RESULT_BACKEND", 'redis://localhost:6379/0'),
)

celery.conf.update(
    timezone='Asia/Karachi',
    enable_utc=False,
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    beat_schedule={
        'fetch-and-store-cars-every-5-minutes': {
            'task': 'tasks_sync_fetch_and_store_cars',
            'schedule': timedelta(minutes=5),
        },
    }
)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

celery.autodiscover_tasks(['tasks'])

print("[CELERY CONFIG] Celery app initialized and beat schedule registered.")
