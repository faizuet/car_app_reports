# Car App Reports 🚗📊  

A Flask-based web application for managing car-related reports with JWT authentication, background task processing using Celery, and Dockerized deployment. Now configured to use **MySQL** as the main database.  

## Features  
- User authentication with JWT  
- Role-based access control  
- **MySQL database with SQLAlchemy ORM**  
- Background tasks with Celery + Redis  
- RESTful API with Marshmallow serialization  
- Docker & Docker Compose setup  
- Configurable via `.env`  

## Project Structure  
```
car_app_reports/
├── app/
│   ├── __init__.py           # App factory setup
│   ├── config.py             # App configs + env variables
│   ├── extensions.py         # db, jwt, ma, migrate instances
│   ├── models/               # Database models
│   │    ├── __init__.py
│   │    ├── car.py
│   │    └── user.py
│   ├── routes/               # API routes
│   ├── tasks/                # Celery tasks
│   └── utils/                # Helper functions
├── docker/
│   ├── Dockerfile            # Flask app image
│   ├── docker-compose.yml    # Multi-container setup
│   └── celery_worker.Dockerfile
├── migrations/               # Database migrations
├── run.py                    # App entry point
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```  

## Installation  

### Prerequisites  
- Python 3.9+  
- MySQL 8.0+  
- Redis (for Celery)  
- Docker & Docker Compose (optional but recommended)  

### Local Setup  
```bash
git clone https://github.com/yourusername/car_app_reports.git
cd car_app_reports

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
SQLALCHEMY_DATABASE_URI=mysql+pymysql://username:password@localhost:3306/car_db
```

Run migrations:  
```bash
flask db upgrade
```

Start the app:  
```bash
python run.py
```

### With Docker  
```bash
docker-compose up --build
```

This will start:  
- Flask app (on http://localhost:5000)  
- MySQL (on localhost:3306)  
- Redis (for Celery broker)  
- Celery worker & beat scheduler  

## Environment Variables (`.env`)  
```
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=mysql+pymysql://username:password@db:3306/car_db
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## API Endpoints  
| Method | Endpoint          | Description            | Auth |
|--------|------------------|------------------------|------|
| POST   | /auth/register    | Register new user      | No   |
| POST   | /auth/login       | Login & get JWT token  | No   |
| GET    | /cars             | List cars              | Yes  |
| POST   | /cars             | Add new car            | Yes  |
| GET    | /reports          | Fetch reports          | Yes  |

*(Expand as needed for your app.)*  

## Running Celery Tasks  
Start worker manually (if not using Docker):  
```bash
celery -A app.celery_worker.celery worker --loglevel=info
celery -A app.celery_worker.celery beat --loglevel=info
```  
