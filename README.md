# Car Registration Reporting System 🚗

This is a Flask backend application that syncs car data from Back4App and stores it in a local SQLite database.

## Features
- Parse API Integration
- Sync cars (2012-2022)
- Store locally in SQLite
- View all synced cars
- RESTful structure with Blueprints

## Endpoints
- `GET /` — Home
- `GET /sync` — Sync cars from Parse API
- `GET /cars` — List all cars

## How to Run

```bash
pip install -r requirements.txt
python run.py
