import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(basedir, 'instance', 'car_database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')


    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    timezone = 'Asia/Karachi'
    enable_utc = False
