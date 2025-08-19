import os
import logging
from celery import Celery
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

celery = Celery(
    'car_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0'),
    include=['car_tasks.sync_cars']
)

celery.conf.beat_schedule = {
    'sync_car_data_every_5_min': {
        'task': 'car_tasks.sync_cars.sync_car_data',
        'schedule': timedelta(minutes=5),
    },
}

celery.conf.timezone = os.getenv('CELERY_TIMEZONE', 'UTC')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Celery app initialized. Tasks will run only when queued or scheduled.")

