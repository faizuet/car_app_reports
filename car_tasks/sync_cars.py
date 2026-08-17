import json
import logging
import urllib.parse

import requests
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import config
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "X-Parse-Application-Id": config.PARSE_APP_ID,
    "X-Parse-REST-API-Key": config.PARSE_REST_API_KEY,
    "Content-Type": "application/json",
}


def _fetch_all_records() -> list[dict]:
    """Fetch all Back4App records for years 2012-2022 with pagination."""
    where = {
        "Year": {"$gte": config.SYNC_YEAR_MIN, "$lte": config.SYNC_YEAR_MAX},
    }
    where_encoded = urllib.parse.quote_plus(json.dumps(where))
    skip = 0
    limit = 1000
    all_results: list[dict] = []

    while True:
        base_url = config.PARSE_API_URL.split("?")[0]
        url = f"{base_url}?limit={limit}&skip={skip}&where={where_encoded}"
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        batch = response.json().get("results", [])
        if not batch:
            break
        all_results.extend(batch)
        if len(batch) < limit:
            break
        skip += limit

    return all_results


@celery.task(name="car_tasks.sync_cars.sync_car_data")
def sync_car_data() -> None:
    """
    Periodic background task: pull car registration data from Back4App
    and upsert into PostgreSQL (+ Neo4j). Existing records are updated in place.
    """
    session: Session = SessionLocal()

    try:
        try:
            results = _fetch_all_records()
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", "N/A")
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
                source_created_at = datetime.fromisoformat(
                    item["createdAt"].replace("Z", "+00:00")
                )
                source_updated_at = datetime.fromisoformat(
                    item["updatedAt"].replace("Z", "+00:00")
                )

                make = get_or_create_make_sync(session, make_name)
                car_model = get_or_create_model_sync(session, model_name, make.id)

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
                    car.updated_at = source_updated_at
                else:
                    car = create_car_with_model_sync(
                        session,
                        name=model_name,
                        year=year,
                        make_id=make.id,
                        car_model_name=model_name,
                        category=category,
                        user_id=None,
                    )
                    car.external_id = external_id
                    car.created_at = source_created_at
                    car.updated_at = source_updated_at
                    session.flush()

                create_car_node_sync(
                    car_id=car.id,
                    name=car.name,
                    year=car.year,
                    category=car.category or "",
                    make_id=make.id,
                    user_id=0,
                )

            except Exception as exc:
                logger.error("Failed to sync record %s: %s", external_id, exc)

        session.commit()
        logger.info("Sync completed successfully.")

    except Exception as exc:
        session.rollback()
        logger.error("Failed to commit sync changes: %s", exc)
    finally:
        session.close()
