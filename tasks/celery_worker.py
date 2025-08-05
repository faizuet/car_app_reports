from app import create_app
from tasks.celery_app import make_celery
import os

flask_app = create_app()
celery = make_celery(flask_app)

celery.conf.beat_schedule = {
    'sync-cars-every-5-minutes': {
        'task': 'tasks.sync.fetch_and_store_cars',
        'schedule': 300.0,
    },
}
celery.conf.timezone = flask_app.config.get("timezone", "Asia/Karachi")

import tasks.sync
