from pydantic import BaseSettings


class Config(BaseSettings):
    # Project
    PROJECT_NAME: str = "Car App"
    DOCKERIZED: bool = True

    # Database
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    MYSQL_HOST: str = "db"
    MYSQL_PORT: int = 3306

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # Auth
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    ALGORITHM: str = "HS256"

    # Celery
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    CELERY_SYNC_INTERVAL: int = 5

    # Computed URIs
    SQLALCHEMY_DATABASE_URI: str = ""
    ASYNC_SQLALCHEMY_DATABASE_URI: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **values):
        super().__init__(**values)

        # Build DB URIs
        self.SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )
        self.ASYNC_SQLALCHEMY_DATABASE_URI = (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

        # Redis URLs for Celery
        self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        self.CELERY_RESULT_BACKEND = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


config = Config()

