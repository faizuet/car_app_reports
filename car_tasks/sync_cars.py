import os
import json
import urllib.parse
import requests
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.core.db import SessionLocal
from app.models.car_model import Make, CarModel, Car
from car_tasks.celery_app import celery

load_dotenv()

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
def sync_car_data() -> None:
    session: Session = SessionLocal()

    try:
        where = urllib.parse.quote_plus(json.dumps({"Year": {"$gte": 2012, "$lte": 2022}}))
        url = f"{PARSE_API_URL}&where={where}"
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        results = response.json().get("results", [])
    except requests.RequestException as exc:
        logger.error("Back4App request failed: %s", exc)
        session.close()
        return

    if not results:
        logger.info("No records fetched from Back4App.")
        session.close()
        return

    logger.info("Fetched %d records from Back4App.", len(results))

    for item in results:
        external_id = item["objectId"]
        make_name = item["Make"]
        model_name = item["Model"]
        year = item["Year"]
        category = item.get("Category") or ""
        created_at = datetime.fromisoformat(item["createdAt"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(item["updatedAt"].replace("Z", "+00:00"))

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

        car = session.query(Car).filter_by(external_id=external_id).first()

        if car:
            car.year = year
            car.category = category
            car.name = model_name
            car.car_model_id = car_model.id
            car.updated_at = updated_at
        else:
            car = Car(
                external_id=external_id,
                name=model_name,
                car_model_id=car_model.id,
                year=year,
                category=category,
                created_at=created_at,
                updated_at=updated_at,
            )
            session.add(car)

    try:
        session.commit()
        logger.info("Sync completed successfully")
    except Exception as exc:
        session.rollback()
        logger.error("Sync failed: %s", exc)
    finally:
        session.close()

