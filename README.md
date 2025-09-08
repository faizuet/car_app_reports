# Car App Reports  

A **FastAPI-based backend** for managing car-related reports with JWT authentication, background task processing using Celery, and Dockerized deployment. Now configured to use **MySQL** as the main database.  

## Features  
- User authentication with JWT (using FastAPI security)  
- Profile update and management  
- **MySQL database with Async SQLAlchemy ORM + Alembic migrations**  
- Background tasks with **Celery + Redis**  
- **Pydantic schemas** for validation & serialization  
- RESTful API with FastAPI (auto-generated Swagger docs)  
- Docker & Docker Compose setup  
- Configurable via `.env`  

## Project Structure  
```
car_app_fastapi/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── core/                   # Core configs, db setup
│   ├── models/                 # SQLAlchemy ORM models
│   │    ├── car_model.py
│   │    └── user_model.py
│   ├── routers/                # API routes (auth, users, cars, etc.)
│   ├── schemas/                # Pydantic schemas
│   ├── utils/                  # Helpers (pagination, etc.)
│   └── deps/                   # Dependencies (auth, security)
├── alembic/                    # Database migrations
├── scripts/                    # Startup scripts
├── docker/                     # Docker-related files
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```  

## Installation  

### Prerequisites  
- Python 3.10+  
- MySQL 8.0+  
- Redis (for Celery)  
- Docker & Docker Compose (recommended)  

### Local Setup  
```bash
git clone https://github.com/faizuet/car_app_reports.git
cd car_app_fastapi

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
```

### Configure MySQL Database  
Make sure you create the database and user:  
```sql
CREATE DATABASE car_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'username'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON car_db.* TO 'username'@'%';
FLUSH PRIVILEGES;
```

Update your `.env` file:  
```env
DATABASE_URL=mysql+aiomysql://username:password@db:3306/car_db
SECRET_KEY=your_secret_key
```

Run migrations:  
```bash
alembic upgrade head
```

Start the app:  
```bash
uvicorn app.main:app --reload
```

### With Docker  
```bash
docker-compose up --build
```

This will start:  
- **FastAPI app** (http://localhost:8000, docs at `/docs`)  
- **MySQL** (on localhost:3307 if mapped)  
- **Redis** (for Celery broker)  
- **Celery worker & beat scheduler**  

## API Endpoints  
| Method | Endpoint         | Description                | Auth |
|--------|-----------------|----------------------------|------|
| POST   | /auth/signup     | Register new user          | No   |
| POST   | /auth/login      | Login & get JWT token      | No   |
| GET    | /users/me        | Get current user profile   | Yes  |
| PUT    | /users/me        | Update current user        | Yes  |
| GET    | /cars            | List cars (paginated)      | Yes  |
| POST   | /cars            | Add new car                | Yes  |

*(expand with reports, tasks, etc. as you implement)*  
