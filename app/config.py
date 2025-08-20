import os
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(BASEDIR, '.env'))

class Config:
    MYSQL_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD', 'Myroot123')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DB = os.getenv('MYSQL_DATABASE', 'car_app_db')

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv(
        'SQLALCHEMY_TRACK_MODIFICATIONS', 'False'
    ).lower() == 'true'

    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
    CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'Asia/Karachi')
    CELERY_ENABLE_UTC = os.getenv('CELERY_ENABLE_UTC', 'False').lower() == 'true'

