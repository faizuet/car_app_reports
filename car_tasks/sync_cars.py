import logging
from datetime import datetime, timezone
import os
import requests
import time
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.mysql import insert as mysql_insert
from car_tasks.celery_app import celery

load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = quote_plus(os.getenv("MYSQL_ROOT_PASSWORD", "Myroot123"))
MYSQL_HOST = os.getenv("MYSQL_HOST", "db")
MYSQL_DB = os.getenv("MYSQL_DATABASE", "car_app_db")
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DB}"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True)
    car_id = Column(String(50), unique=True, nullable=False)
    objectId = Column(String(255), nullable=False, unique=True)
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

Base.metadata.create_all(bind=engine)

PARSE_API_URL = os.getenv("PARSE_API_URL")
PARSE_APP_ID = os.getenv("PARSE_APP_ID")
PARSE_MASTER_KEY = os.getenv("PARSE_MASTER_KEY")

if not PARSE_APP_ID or not PARSE_MASTER_KEY:
    raise RuntimeError("PARSE_APP_ID and PARSE_MASTER_KEY must be set in .env")

HEADERS = {
    "X-Parse-Application-Id": PARSE_APP_ID,
    "X-Parse-Master-Key": PARSE_MASTER_KEY,
    "Content-Type": "application/json",
}

def _to_int_or_none(value):
    try:
        return int(value) if value else None
    except (TypeError, ValueError):
        return None

@celery.task(name="car_tasks.sync_cars.fetch_and_store_cars")
def fetch_and_store_cars():
    now = datetime.now(timezone.utc)
    batch_size = 500
    max_retries = 3

    try:
        results = requests.get(PARSE_API_URL, headers=HEADERS, timeout=30).json().get("results", [])
    except requests.RequestException as exc:
        logger.error("Back4App request failed: %s", exc)
        return

    if not results:
        logger.info("No records fetched from Back4App.")
        return

    logger.info("Sample API response: %s", results[0] if results else "No results")
    logger.info("Fetched %d records from Back4App.", len(results))

    with SessionLocal() as session:
        for start in range(0, len(results), batch_size):
            batch = results[start:start + batch_size]
            records = []

            for item in batch:
                object_id = item.get("objectId")
                if not object_id:
                    continue

                records.append({
                    "car_id": object_id,
                    "objectId": object_id,
                    "make": item.get("Make"),
                    "model": item.get("Model"),
                    "category": item.get("Category"),
                    "year": _to_int_or_none(item.get("Year")),
                    "created_at": now,
                    "updated_at": now
                })

            if not records:
                continue

            for attempt in range(max_retries):
                try:
                    stmt = mysql_insert(Car).values(records)
                    stmt = stmt.on_duplicate_key_update(
                        make=stmt.inserted.make,
                        model=stmt.inserted.model,
                        category=stmt.inserted.category,
                        year=stmt.inserted.year,
                        updated_at=stmt.inserted.updated_at
                    )
                    session.execute(stmt)
                    session.commit()
                    logger.info("Batch %d-%d synced (%d records)", start + 1, start + len(batch), len(records))
                    break
                except Exception as exc:
                    session.rollback()
                    wait_time = 2 ** attempt
                    logger.warning(
                        "Batch sync failed on attempt %d/%d: %s. Retrying in %ds...",
                        attempt + 1, max_retries, exc, wait_time
                    )
                    time.sleep(wait_time)
            else:
                logger.error("Batch %d-%d failed after %d retries.", start + 1, start + len(batch), max_retries)

    logger.info("Sync completed. Total records processed: %d", len(results))

