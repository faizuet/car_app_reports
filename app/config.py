import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(basedir, '.env'))

class Config:

    SQLALCHEMY_DATABASE_URI = (
        os.getenv("SQLALCHEMY_DATABASE_URI") or
        os.getenv("DATABASE_URL") or
        f"sqlite:///{os.path.join(basedir, 'instance', 'car_database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'Asia/Karachi')
    CELERY_ENABLE_UTC = os.getenv('CELERY_ENABLE_UTC', 'False').lower() == 'true'

