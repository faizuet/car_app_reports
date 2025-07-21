import requests

def fetch_all_cars():
    url = "https://parseapi.back4app.com/classes/Car_Model_List?limit=10000"
    headers = {
        "X-Parse-Application-Id": "hlhoNKjOvEhqzcVAJ1lxjicJLZNVv36GdbboZj3Z",
        "X-Parse-Master-Key": "SNMJJF0CZZhTPhLDIqGhTlUNV9r60M2Z5spyWfXW"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print("Failed to fetch cars from Parse API")
        return []
