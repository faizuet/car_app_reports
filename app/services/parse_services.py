import requests
from datetime import datetime

PARSE_URL = "https://parseapi.back4app.com/classes/Car_Model_List?limit=10000"
HEADERS = {
    "X-Parse-Application-Id": "hlhoNKjOvEhqzcVAJ1lxjicJLZNVv36GdbboZj3Z",
    "X-Parse-Master-Key": "SNMJJF0CZZhTPhLDIqGhTlUNV9r60M2Z5spyWfXW"
}


def fetch_all_cars():
    response = requests.get(PARSE_URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from Parse API")

    all_cars = response.json().get("results", [])

    # Filter cars from year 2012 to 2022
    filtered = [
        {
            "object_id": car.get("objectId"),
            "make": car.get("Make"),
            "model": car.get("Model"),
            "year": int(car.get("Year")),
            "created_at": car.get("createdAt")
        }
        for car in all_cars
        if car.get("Year") and 2012 <= int(car["Year"]) <= 2022
    ]
    return filtered
