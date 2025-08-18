import logging
import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv


load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "Asia/Karachi")
CELERY_ENABLE_UTC = False

celery = Celery(
    "car_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["car_tasks.sync_cars"],
)

celery.conf.update(
    timezone=CELERY_TIMEZONE,
    enable_utc=CELERY_ENABLE_UTC,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_always_eager=False,
)

celery.conf.beat_schedule = {
    "sync-cars-every-5-mins": {
        "task": "car_tasks.sync_cars.fetch_and_store_cars",
        "schedule": crontab(minute="*/5"),
    }
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Celery app ready. Tasks will only run when scheduled or queued.")

