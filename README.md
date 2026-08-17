# Car Registration Reports API

A **FastAPI** backend for a car registration reporting app. It syncs vehicle data from the [Back4App Car Models dataset](https://www.back4app.com/database/back4app/car-make-model-dataset), stores it in a normalized **PostgreSQL** database, and exposes authenticated REST APIs for users to search and view reports.

This project implements the **Python Real World Challenge** requirements using **FastAPI** (instead of Flask) with **Pydantic** for schema validation (equivalent to Marshmallow).

---

## Challenge Requirements Mapping

| Requirement | Implementation |
|-------------|----------------|
| Sign up / Login | `POST /auth/signup`, `POST /auth/login` with JWT |
| Periodic dataset sync (daily, 2012–2022) | Celery Beat task `sync_car_data` runs once per day |
| Upsert (update, not overwrite) | Records matched by `external_id` from Back4App |
| Search reports by make, model, year, date | `GET /reports/` with query filters + pagination |
| Schema validation | Pydantic models on all request/response bodies |
| Pagination | Cursor-based pagination on list/search endpoints |
| Database normalization | `Make` → `CarModel` → `Car` tables |
| User authentication | JWT bearer tokens verified on protected routes |

---

## Tech Stack

- **FastAPI** + Uvicorn
- **PostgreSQL** (SQLAlchemy 2.0 + Alembic)
- **Neo4j** (optional graph mirror for cars/users)
- **Celery** + **Redis** (background sync)
- **Pydantic v2** (validation)
- **Docker Compose** (full stack)

---

## API Endpoints

All protected routes require: `Authorization: Bearer <token>`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/auth/signup` | No | Register a new user |
| POST | `/auth/login` | No | Login and receive JWT |
| GET | `/users/me` | Yes | Current user profile |
| PUT | `/users/me` | Yes | Update current user profile |
| GET | `/reports/` | Yes | **Search car registration reports** |
| GET | `/cars/` | Yes | List user's own cars (paginated) |
| POST | `/cars/` | Yes | Add a user-owned car |
| GET | `/cars/{id}` | Yes | Get a user-owned car |
| PATCH | `/cars/{id}` | Yes | Partially update a car |
| PUT | `/cars/{id}` | Yes | Replace a car |
| DELETE | `/cars/{id}` | Yes | Delete a car |

**Interactive docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Search Reports Example

```http
GET /reports/?make=Toyota&model=Corolla&year=2020&date_from=2019-01-01T00:00:00&limit=10
Authorization: Bearer <your_token>
```

**Query parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `make` | string | Partial match on manufacturer |
| `model` | string | Partial match on model name |
| `year` | int | Manufacturing year (2012–2022) |
| `date_from` | datetime | Report created on or after |
| `date_to` | datetime | Report created on or before |
| `limit` | int | Page size (1–100, default 10) |
| `cursor` | int | Last seen `id` for next page |

---

## Database Schema

```
makes (id, name)
car_models (id, name, make_id → makes.id)
cars (id, name, year, category, car_model_id, user_id, external_id, created_at, updated_at)
users (id, username, email, password_hash, created_at, updated_at)
```

- Synced Back4App records have a non-null `external_id`.
- User-created cars have `user_id` set and typically no `external_id`.

---

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Key variables:

```env
ENV=local
JWT_SECRET_KEY=your-secret-key-here

# PostgreSQL
POSTGRES_USER=appuser
POSTGRES_PASSWORD=AppPass123
POSTGRES_DB=car_app_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Neo4j
NEO4J_USER=neo4j
NEO4J_PASSWORD=Neo4j_1234

# Back4App (defaults match challenge credentials)
PARSE_APP_ID=gP38fEGPgSSBvvO4Kz9McQD2UpUrcpIlrXDyHLWc
PARSE_REST_API_KEY=72gJMaTFClPr90oA7bkRYdUy0PJIcKQ8tj8bQvtP
PARSE_API_URL=https://parseapi.back4app.com/classes/Carmodels_Car_Model_List?limit=1000

# Celery daily sync (UTC)
CELERY_SYNC_HOUR=0
CELERY_SYNC_MINUTE=0
SYNC_YEAR_MIN=2012
SYNC_YEAR_MAX=2022
```

For Docker Compose, set `ENV=docker` (or rely on `docker-compose.yaml` which sets it for app services).

---

## Running Locally (Recommended for Testing)

### Option A — App on your machine, databases in Docker

This is the easiest way to develop and test on Windows.

**1. Start PostgreSQL, Redis, and Neo4j:**

```bash
docker compose up db redis neo4j -d
```

**2. Create virtualenv and install dependencies:**

```bash
cd car_app_reports
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

**3. Configure environment:**

```bash
copy .env.example .env
```

Ensure `.env` has `ENV=local` and `POSTGRES_HOST=localhost`.

**4. Create database tables:**

```bash
alembic upgrade head
```

**5. Start the API:**

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs)

**6. Start Celery (two extra terminals, venv activated):**

```bash
celery -A car_tasks.celery_app worker --loglevel=info
```

```bash
celery -A car_tasks.celery_app beat --loglevel=info
```

**7. Trigger a manual data sync (optional, for report data):**

```bash
celery -A car_tasks.celery_app call car_tasks.sync_cars.sync_car_data
```

---

### Option B — Full stack in Docker

```bash
copy .env.example .env
docker compose up --build
```

API: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Prerequisites

- Python 3.10+
- Docker Desktop (for PostgreSQL, Redis, Neo4j)

---

## Project Structure

```
car_app_reports/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── core/                   # Config, DB engines
│   ├── models/                 # SQLAlchemy models
│   ├── routers/                # Route handlers
│   │   ├── auth_routes.py      # Signup / login
│   │   ├── reports_routes.py   # Search reports (challenge)
│   │   ├── cars_routes.py      # User car CRUD
│   │   └── users_routes.py     # User profile
│   ├── schemas/                # Pydantic validation
│   ├── utils/                  # Services, pagination, Neo4j
│   └── deps/                   # JWT auth dependency
├── car_tasks/
│   ├── celery_app.py           # Celery + daily beat schedule
│   └── sync_cars.py            # Back4App sync task
├── alembic/                    # DB migrations
├── scripts/                    # Docker startup scripts
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── README.md
└── REPORT.md                   # Challenge submission report
```

---

## Testing with Postman

1. **Sign up:** `POST /auth/signup` with `{ "username", "email", "password" }`
2. **Login:** `POST /auth/login` with `{ "email", "password" }` → copy `access_token`
3. **Search reports:** `GET /reports/?make=Ford&year=2018` with Bearer token
4. Wait for Celery sync (or trigger manually) before reports contain data

---

## License

MIT
