import logging
from datetime import timedelta
from celery import Celery
from app.core.config import config

celery = Celery(
    "car_tasks",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=["car_tasks.sync_cars"],
)

celery.conf.beat_schedule_filename = "celerybeat-schedule.json"

celery.conf.beat_schedule = {
    "sync_car_data_every_interval": {
        "task": "car_tasks.sync_cars.sync_car_data",
        "schedule": timedelta(minutes=config.CELERY_SYNC_INTERVAL),
    }
}

celery.conf.timezone = "UTC"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(
    "Celery app initialized with broker %s (sync interval: %s minutes)",
    config.CELERY_BROKER_URL,
    config.CELERY_SYNC_INTERVAL,
)

