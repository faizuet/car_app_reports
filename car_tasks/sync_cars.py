import json
import urllib.parse
import requests
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from app.core.sync_db import SessionLocal
from app.models.car_model import Car
from car_tasks.celery_app import celery
from app.utils.services import (
    get_or_create_make_sync,
    get_or_create_model_sync,
    create_car_with_model_sync,
    update_car_data_sync,
)
from app.utils.neo4j_service import create_car_node_sync

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Back4App config
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
        # Fetch records from Back4App
        where = urllib.parse.quote_plus(json.dumps({"Year": {"$gte": 2012, "$lte": 2022}}))
        url = f"{PARSE_API_URL}&where={where}"

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            results = response.json().get("results", [])
        except requests.RequestException as exc:
            status = getattr(exc.response, "status_code", "N/A")
            logger.error("Back4App request failed (status=%s): %s", status, exc)
            return

        if not results:
            logger.info("No records fetched from Back4App.")
            return

        logger.info("Fetched %d records from Back4App.", len(results))

        for item in results:
            external_id = item.get("objectId")
            try:
                make_name = item["Make"]
                model_name = item["Model"]
                year = item["Year"]
                category = item.get("Category")
                created_at = datetime.fromisoformat(item["createdAt"].replace("Z", "+00:00"))
                updated_at = datetime.fromisoformat(item["updatedAt"].replace("Z", "+00:00"))

                # Upsert Make and CarModel using sync service
                make = get_or_create_make_sync(session, make_name)
                car_model = get_or_create_model_sync(session, model_name, make.id)

                # Upsert Car
                car = session.query(Car).filter_by(external_id=external_id).first()
                if car:
                    car = update_car_data_sync(
                        session,
                        car,
                        data={
                            "name": model_name,
                            "year": year,
                            "category": category,
                        },
                        car_model_name=model_name,
                        make_id=make.id,
                    )
                else:
                    car = create_car_with_model_sync(
                        session,
                        name=model_name,
                        year=year,
                        make_id=make.id,
                        car_model_name=model_name,
                        category=category,
                        user_id=0,  # or assign user if available
                    )
                    # save external_id
                    car.external_id = external_id
                    session.flush()

                # Mirror to Neo4j
                create_car_node_sync(
                    car_id=car.id,
                    name=car.name,
                    year=car.year,
                    category=car.category or "",
                    make_id=make.id,
                    user_id=car.user_id or 0,
                )

            except Exception as exc:
                logger.error("Failed to sync record %s: %s", external_id, exc)

        # Commit all MySQL changes
        try:
            session.commit()
            logger.info("Sync completed successfully.")
        except Exception as exc:
            session.rollback()
            logger.error("Failed to commit changes: %s", exc)

    finally:
        session.close()

