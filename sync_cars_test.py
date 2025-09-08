import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

PARSE_API_URL = os.getenv("PARSE_API_URL")
PARSE_APP_ID = os.getenv("PARSE_APP_ID")
PARSE_MASTER_KEY = os.getenv("PARSE_MASTER_KEY")

HEADERS = {
    "X-Parse-Application-Id": PARSE_APP_ID,
    "X-Parse-Master-Key": PARSE_MASTER_KEY,
    "Content-Type": "application/json",
}

response = requests.get(PARSE_API_URL, headers=HEADERS, timeout=30)
response.raise_for_status()

data = response.json().get("results", [])
print(json.dumps(data, indent=4))

