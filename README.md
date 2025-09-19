# Car Application

A **FastAPI-based REST API** for managing car registration data with a scalable architecture using both **MySQL** (relational data) and **Neo4j** (graph relationships). The app supports secure JWT authentication, handles background tasks with Celery, and is fully containerized with Docker.  

---

## Features  

- **Modern Tech Stack**: Built with FastAPI for high performance.  
- **Hybrid Database**: MySQL for relational data + Neo4j for graph-based relationships.  
- **JWT Authentication**: Secure endpoints with `POST /auth/signup` and `POST /auth/login`.  
- **Full CRUD Operations**: Manage users, cars, and related entities.  
- **Graph Queries**: Explore relationships between cars, makes, and models in Neo4j.  
- **Background Tasks**: Sync data syncing handled by Celery with Redis.  
- **Containerized Deployment**: Easy setup with Docker & Docker Compose.  
- **Schema Validation**: Pydantic ensures data integrity.  

---

## Tech Stack  

- **Backend**: FastAPI, Uvicorn  
- **Databases**: MySQL (SQLAlchemy + Alembic), Neo4j  
- **Authentication**: JWT (python-jose)  
- **Task Queue**: Celery, Redis  
- **Validation**: Pydantic  
- **Containerization**: Docker & Docker Compose  

---

## API Endpoints  

All car endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.  

| Method | Route          | Auth | Description                   |
|--------|----------------|------|-------------------------------|
| POST   | `/auth/signup` | No   | Register a new user           |
| POST   | `/auth/login`  | No   | Login & get JWT token         |
| GET    | `/users/me`    | Yes  | Get current user profile      |
| PUT    | `/users/me`    | Yes  | Update current user profile   |
| GET    | `/cars`        | Yes  | List all cars (paginated)     |
| POST   | `/cars`        | Yes  | Add a new car                 |
| GET    | `/cars/graph`  | Yes  | Get car relationships (Neo4j) |

**API Documentation:** `http://localhost:8000/docs`  

---

## Database Schema  

- **MySQL**: Stores user accounts, authentication, and core car data.  
- **Neo4j**: Stores graph relationships:  
  - **Nodes**: `(:User)`, `(:Car)`, `(:Make)`, `(:Model)`  
  - **Relationships**:  
    - `(:Car)-[:HAS_MODEL]->(:Model)`  
    - `(:Model)-[:HAS_MAKE]->(:Make)`  

---

## Setup (Local Development)  

### Prerequisites  
- Python 3.10+  
- MySQL 8.0+  
- Neo4j 5.x+  
- Redis  
- Docker & Docker Compose  

### Clone & Setup  
```bash
git clone https://github.com/faizuet/car_app_reports.git
cd car_app_fastapi
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```  

### Environment File  
Create a `.env` file in the project root:  
```env
SECRET_KEY=your-secret-key

# MySQL
DATABASE_URL=mysql+aiomysql://username:password@db:3306/car_db

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Celery / Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```  

### Start Services (Local)  
```bash
# Run migrations for MySQL
alembic upgrade head

# Start FastAPI
uvicorn app.main:app --reload
```  

---

## Docker Setup  

Update `.env` for Docker networking:  
```env
DATABASE_URL=mysql+aiomysql://username:password@mysql:3306/car_db
NEO4J_URI=bolt://neo4j:7687
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```  

Then run:  
```bash
docker compose up --build
```  

This will start:  
- FastAPI backend  
- MySQL  
- Neo4j (http://localhost:7474)  
- Redis  
- Celery worker + beat  

---

## Project Structure  

```
car_app_fastapi/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── core/                   # Configs, DB setup
│   │   ├── async_db.py
│   │   ├── sync_db.py
│   │   ├── config.py
│   │   └── base.py
│   ├── models/                 # SQLAlchemy models
│   │   ├── car_model.py
│   │   └── user_model.py
│   ├── routers/                # API routes
│   │   ├── auth_routes.py
│   │   ├── cars_routes.py
│   │   └── users_routes.py
│   ├── schemas/                # Pydantic schemas
│   ├── utils/                  # Helpers & Neo4j services
│   └── deps/                   # Dependencies (auth, etc.)
├── car_tasks/                  # Celery tasks
│   ├── celery_app.py
│   └── sync_cars.py
├── alembic/                    # DB migrations
├── scripts/                    # Startup scripts
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```
