import requests
from datetime import datetime, timezone

PARSE_URL = "https://parseapi.back4app.com/classes/Car_Model_List?limit=10000"
HEADERS = {
    "X-Parse-Application-Id": "hlhoNKjOvEhqzcVAJ1lxjicJLZNVv36GdbboZj3Z",
    "X-Parse-Master-Key": "SNMJJF0CZZhTPhLDIqGhTlUNV9r60M2Z5spyWfXW"
}

def fetch_all_cars():
    try:
        response = requests.get(PARSE_URL, headers=HEADERS)
        response.raise_for_status()
        all_cars = response.json().get("results", [])

        filtered = []
        for car in all_cars:
            year = car.get("Year")
            if year and 2012 <= int(year) <= 2022:
                try:
                    created_at = datetime.strptime(car.get("createdAt"), "%Y-%m-%dT%H:%M:%S.%fZ")
                    created_at = created_at.replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    created_at = datetime.now(timezone.utc)

                filtered.append({
                    "parse_id": car.get("objectId"),  # Matching DB field
                    "make": car.get("Make", "Unknown"),
                    "model": car.get("Model", "Unknown"),
                    "year": int(year),
                    "created_at": created_at
                })

        return filtered

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error while fetching cars: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error occurred: {str(e)}")
