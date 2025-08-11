from tasks.celery_app import celery
from app import create_app  
from app.models.car import Car
from app.extensions import db
import requests
from datetime import datetime, timezone

PARSE_API_URL = "https://parseapi.back4app.com/classes/Car_Model_List?limit=10000"
HEADERS = {
    "X-Parse-Application-Id": "hlhoNKjOvEhqzcVAJ1lxjicJLZNVv36GdbboZj3Z",
    "X-Parse-Master-Key": "SNMJJF0CZZhTPhLDIqGhTlUNV9r60M2Z5spyWfXW",
    "Content-Type": "application/json",
}

app = create_app()

@celery.task(name="tasks_sync_fetch_and_store_cars") 
def fetch_and_store_cars():
    with app.app_context():
        print("[CELERY TASK] Fetching car data from Parse API...")

        try:
            response = requests.get(PARSE_API_URL, headers=HEADERS)
            if response.status_code != 200:
                print(f"[ERROR] Failed to fetch data: {response.text}")
                return {"status": "error", "message": "Failed to fetch data"}

            data = response.json().get("results", [])

            inserted_count = 0
            skipped_count = 0
            updated_count = 0

            for item in data:
                car_id = item.get("car_id") or item.get("CarID") or f"{item.get('Make','')}-{item.get('Model','')}"
                existing = Car.query.filter_by(objectId=item["objectId"]).first()

                if existing:
                    updated = False
                    if existing.make != item.get("Make"):
                        existing.make = item.get("Make")
                        updated = True
                    if existing.model != item.get("Model"):
                        existing.model = item.get("Model")
                        updated = True
                    if existing.category != item.get("Category"):
                        existing.category = item.get("Category")
                        updated = True
                    if existing.year != item.get("Year"):
                        existing.year = item.get("Year")
                        updated = True
                    if updated:
                        updated_count += 1
                else:
                    car = Car(
                        car_id=car_id,
                        objectId=item["objectId"],
                        name=item.get("Name") or f"{item.get('Make','')} {item.get('Model','')}",
                        make=item.get("Make"),
                        model=item.get("Model"),
                        year=item.get("Year") or 0,
                        category=item.get("Category"),
                        created_at=item.get("createdAt") and datetime.fromisoformat(
                            item["createdAt"].replace("Z", "+00:00")
                        )
                    )
                    db.session.add(car)
                    inserted_count += 1

            db.session.commit()
            skipped_count = len(data) - (inserted_count + updated_count)

            print(f"[SYNC COMPLETE] Inserted: {inserted_count}, Updated: {updated_count}, Skipped: {skipped_count}")
            return {
                "status": "success",
                "inserted": inserted_count,
                "updated": updated_count,
                "skipped": skipped_count
            }

        except Exception as e:
            print(f"[EXCEPTION] {str(e)}")
            return {"status": "error", "message": str(e)}
