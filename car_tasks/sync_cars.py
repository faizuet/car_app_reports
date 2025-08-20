from car_tasks.celery_app import celery
import os, json, urllib.parse, requests, logging
from datetime import datetime, timezone
from app.models.db import SessionLocal
from app.models.car import Make, CarModel, Car

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PARSE_API_URL = os.getenv("PARSE_API_URL")
PARSE_APP_ID = os.getenv("PARSE_APP_ID")
PARSE_MASTER_KEY = os.getenv("PARSE_MASTER_KEY")

HEADERS = {
    "X-Parse-Application-Id": PARSE_APP_ID,
    "X-Parse-Master-Key": PARSE_MASTER_KEY,
    "Content-Type": "application/json",
}

@celery.task(name="car_tasks.sync_cars.sync_car_data")
def sync_car_data():
    session = SessionLocal()
    now = datetime.now(timezone.utc)
    batch_size = 500

    try:
        where = urllib.parse.quote_plus(json.dumps({"Year": {"$gte": 2012, "$lte": 2022}}))
        url = f"{PARSE_API_URL}&where={where}"
        results = requests.get(url, headers=HEADERS, timeout=30).json().get("results", [])
    except requests.RequestException as exc:
        logger.error("Back4App request failed: %s", exc)
        return

    if not results:
        logger.info("No records fetched from Back4App.")
        return

    logger.info("Fetched %d records from Back4App.", len(results))

    for start in range(0, len(results), batch_size):
        batch = results[start:start + batch_size]

        for item in batch:
            make_name = item.get("Make")
            model_name = item.get("Model")
            year = item.get("Year")
            category = item.get("Category") or ""

            if not all([make_name, model_name, year]):
                continue

            make = session.query(Make).filter_by(name=make_name).first()
            if not make:
                make = Make(name=make_name)
                session.add(make)
                session.flush()

            car_model = session.query(CarModel).filter_by(name=model_name, make_id=make.id).first()
            if not car_model:
                car_model = CarModel(name=model_name, make_id=make.id)
                session.add(car_model)
                session.flush()

            car = session.query(Car).filter_by(make_id=make.id, model_id=car_model.id, year=year).first()
            if not car:
                car = Car(make_id=make.id, model_id=car_model.id, year=year, category=category)
                session.add(car)

        try:
            session.commit()
            logger.info("Batch %d-%d synced", start + 1, start + len(batch))
        except Exception as exc:
            session.rollback()
            logger.error("Batch %d-%d failed: %s", start + 1, start + len(batch), exc)

    session.close()

