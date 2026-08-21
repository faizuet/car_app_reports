# Car Registration Reports — Project Report

## 1. Overview

This document describes the architecture, design decisions, and implementation of the **Car Registration Reports** application, built as a response to the Python Real World Challenge. The challenge specified Flask; this implementation uses **FastAPI**, which provides equivalent REST capabilities with built-in **Pydantic** validation (replacing Marshmallow) and automatic OpenAPI documentation.

The application allows users to register, log in, and search car registration reports that are synced daily from the Back4App public dataset into a local PostgreSQL database. A **React + TypeScript** frontend provides a full UI for auth, reports search, user cars, and profile management.

---

## 2. Code Structure

### 2.1 Layered Architecture

```
Routers (HTTP)  →  Services (business logic)  →  Models (SQLAlchemy ORM)
                 ↘  Schemas (Pydantic validation)
                 ↘  Dependencies (JWT auth)
```

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Entry point** | `app/main.py` | FastAPI app, CORS, static uploads, router registration |
| **Configuration** | `app/core/config.py` | Environment-driven settings (DB, JWT, Back4App, Celery) |
| **Routers** | `app/routers/` | HTTP endpoints, request/response mapping |
| **Schemas** | `app/schemas/` | Input/output validation and serialization |
| **Models** | `app/models/` | Normalized relational schema |
| **Services** | `app/utils/services.py` | Reusable DB operations (async for API, sync for Celery) |
| **Background tasks** | `car_tasks/` | Celery worker and scheduled sync |
| **Auth** | `app/deps/auth.py` | JWT creation, verification, password hashing |
| **Frontend** | `frontend/` | React 18 + Vite + Tailwind UI |

### 2.2 Database Normalization

The car dataset is stored in third normal form (3NF):

- **`makes`** — unique manufacturers (e.g. Toyota, Ford)
- **`car_models`** — models linked to a make (e.g. Corolla → Toyota)
- **`cars`** — individual registration records with year, category, timestamps
- **`users`** — application accounts with bcrypt-hashed passwords

Synced records from Back4App are identified by `external_id` (Parse `objectId`). This enables **upsert** behavior: existing records are updated in place rather than deleted and re-inserted.

### 2.3 Authentication Flow

1. User registers via `POST /auth/signup` — password is hashed with bcrypt before storage.
2. User logs in via `POST /auth/login` — credentials are verified; a JWT access token is returned.
3. Protected routes use the `get_current_user` dependency, which decodes and validates the JWT on every request.
4. Invalid or expired tokens receive `401 Unauthorized`.

---

## 3. Challenge Requirements — Implementation Details

### 3.1 Sign Up / Login

- **Files:** `app/routers/auth_routes.py`, `app/models/user_model.py`, `app/schemas/user_schema.py`
- Passwords are never stored in plain text; `passlib` with bcrypt is used.
- Email uniqueness is enforced at registration time.

### 3.2 Periodic Sync of Dataset

- **Files:** `car_tasks/sync_cars.py`, `car_tasks/celery_app.py`
- **Schedule:** Once per day at 00:00 UTC via Celery Beat (`crontab`).
- **Data source:** Back4App REST API with challenge-provided credentials.
- **Year filter:** Only records with `Year` between 2012 and 2022 are fetched.
- **Upsert logic:**
  - If `external_id` exists → update fields (`name`, `year`, `category`, model relation, `updated_at`).
  - If new → insert with `created_at` / `updated_at` from Back4App.
- **Pagination:** The sync task paginates through the API (`skip` / `limit`) until all matching records are retrieved.

### 3.3 Search Functionality

- **File:** `app/routers/reports_routes.py`
- **Endpoint:** `GET /reports/`
- **Filters:**
  - `make` — case-insensitive partial match
  - `model` — case-insensitive partial match
  - `year` — exact match (2012–2022)
  - `date_from` / `date_to` — filter on `created_at` (registration date from dataset)
- **Auth:** JWT required.
- **Pagination:** Cursor-based (`cursor` + `limit`) with total count in response.

### 3.4 Schema Validation

- **Tool:** Pydantic v2 (native to FastAPI)
- All request bodies (`UserCreateSchema`, `CarCreate`, etc.) and responses (`CarReportRead`, `TokenSchema`, etc.) are validated automatically.
- Query parameters for search are validated via `CarSearchQuery`.

---

## 4. Additional Design Choices

### 4.1 FastAPI Instead of Flask

FastAPI was chosen for:
- Native async support (better concurrency for I/O-bound DB/API calls)
- Automatic OpenAPI/Swagger docs at `/docs`
- Pydantic integration (no separate Marshmallow setup)

The routing, blueprints, and request handling patterns map directly from Flask concepts to FastAPI routers.

### 4.2 React Frontend (Extension)

The `frontend/` directory adds a professional UI beyond the challenge minimum:

| Feature | Description |
|---------|-------------|
| Auth | Login, signup, JWT storage, 401 auto-logout, post-login redirect |
| Reports | Filter by make/model/year/date, URL-synced filters, grid/list view, detail modal |
| My Cars | Add, edit, delete user cars with make/model dropdowns from synced data |
| Profile | Avatar upload, display name, bio, email, password change |

Run via Docker (`docker compose up frontend`) or locally with `scripts/start_frontend.ps1`.

### 4.3 Neo4j Graph Mirror (Extension)

The codebase optionally mirrors users and cars into Neo4j for graph relationship queries. This is **beyond the challenge scope** but demonstrates hybrid storage patterns. The core challenge features work entirely through PostgreSQL.

### 4.4 User-Owned Cars vs Synced Reports

- **`GET /reports/`** — searches synced Back4App data (`external_id IS NOT NULL`)
- **`GET /cars/`** — lists cars created by the authenticated user
- **`GET /makes/`** — lists manufacturers from synced data (used by the Cars UI)

This separation keeps the challenge's "reports" use case distinct from optional user CRUD features.

---

## 5. Problems Faced & Solutions

| Problem | Solution |
|---------|----------|
| Challenge specified Flask/Marshmallow | Used FastAPI/Pydantic — functionally equivalent, better DX |
| Back4App returns paginated results | Implemented skip/limit loop in `_fetch_all_records()` |
| "Update not overwrite" requirement | Upsert by `external_id`; preserve original `created_at` on updates |
| Cursor pagination total count with filters | Count via subquery of the filtered base query |
| Sync schedule was every 5 minutes | Changed Celery Beat to daily `crontab` per challenge spec |
| REST API key vs Master key | Switched headers to `X-Parse-REST-API-Key` as documented |
| MySQL → PostgreSQL migration | Rebuilt Alembic migrations for PostgreSQL |
| Docker shell scripts on Windows | CRLF line-ending fix in `docker-compose.yaml` + `.gitattributes` |
| Windows Celery worker | Use `--pool=solo` in local scripts |

---

## 6. How to Run

See [README.md](./README.md) for full setup instructions.

### Quick start with Docker

```bash
docker compose up --build
```

- API docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

### Manual data sync (if reports are empty)

```bash
# With venv activated and DB/Redis running:
celery -A car_tasks.celery_app call car_tasks.sync_cars.sync_car_data
```

Or via Python:

```bash
python -c "from car_tasks.sync_cars import sync_car_data; sync_car_data()"
```

### Test flow (API)

1. **Sign up** — `POST /auth/signup` with `{ "username", "email", "password" }`
2. **Login** — `POST /auth/login` → copy `access_token`
3. **Search reports** — `GET /reports/?make=Toyota&year=2020` with `Authorization: Bearer <token>`
4. **List makes** — `GET /makes/` (for Cars page dropdowns)

Postman collection: `postman/Car_App_Reports.postman_collection.json`

### Test flow (UI)

1. Open http://localhost:5173
2. Create account → log in
3. Go to **Reports** → apply filters (URL updates automatically)
4. Click a report card to view details
5. Go to **My Cars** → add a car using the make/model dropdown
6. Go to **Profile** → update info or upload avatar

### Automated smoke tests

Requires PostgreSQL running (e.g. `docker compose up db -d`):

```bash
pip install -r requirements.txt
pytest
```

Tests cover: health check, auth-required routes, signup/login/profile, reports search, and makes list.

---

## 7. Git Commit History

Commits should reflect incremental development steps, for example:

1. Initial project scaffold (FastAPI, Docker, PostgreSQL)
2. User model + signup/login with JWT
3. Normalized car schema + Alembic migrations
4. Celery sync task for Back4App dataset
5. Reports search API with pagination
6. React frontend (auth, reports, cars, profile)
7. Documentation (README + REPORT) + smoke tests

---

## 8. Conclusion

The project fulfills all challenge requirements using FastAPI: authenticated signup/login, daily background sync of 2012–2022 car data with upsert semantics, searchable reports API with date/make/model/year filters, Pydantic schema validation, normalized PostgreSQL storage, and cursor-based pagination. Docker Compose provides a reproducible environment for evaluation.

The React frontend, profile management, makes API, and pytest smoke tests extend the project beyond the minimum scope while keeping the core challenge features clearly separated and documented.
