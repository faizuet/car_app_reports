import logging
from celery import Celery
from celery.schedules import crontab

from app.core.config import config

# --- Initialize Celery ---
celery = Celery(
    "car_tasks",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=["car_tasks.sync_cars"],
)

# --- Beat schedule: sync once per day (challenge requirement) ---
celery.conf.beat_schedule = {
    "sync_car_data_daily": {
        "task": "car_tasks.sync_cars.sync_car_data",
        "schedule": crontab(
            hour=config.CELERY_SYNC_HOUR,
            minute=config.CELERY_SYNC_MINUTE,
        ),
    }
}
celery.conf.timezone = "UTC"

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(
    "Celery initialized with broker %s (daily sync at %02d:%02d UTC)",
    config.CELERY_BROKER_URL,
    config.CELERY_SYNC_HOUR,
    config.CELERY_SYNC_MINUTE,
)

