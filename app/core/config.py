from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    # Project
    PROJECT_NAME: str = Field("Car App Reports", env="PROJECT_NAME")
    ENV: str = Field("local", env="ENV")  # local | docker

    # PostgreSQL
    POSTGRES_USER: str = Field("appuser", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("AppPass123", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("car_app_db", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")

    # Neo4j
    NEO4J_URI: str = Field("bolt://localhost:7687", env="NEO4J_URI")
    NEO4J_USER: str = Field("neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field("Neo4j_1234", env="NEO4J_PASSWORD")

    # Redis
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")

    # JWT / Auth
    JWT_SECRET_KEY: str = Field(
        "dev-secret-key-change-in-production",
        env="JWT_SECRET_KEY",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")

    # Back4App (car registration dataset)
    PARSE_API_URL: str = Field(
        "https://parseapi.back4app.com/classes/Carmodels_Car_Model_List?limit=1000",
        env="PARSE_API_URL",
    )
    PARSE_APP_ID: str = Field(
        "gP38fEGPgSSBvvO4Kz9McQD2UpUrcpIlrXDyHLWc",
        env="PARSE_APP_ID",
    )
    PARSE_REST_API_KEY: str = Field(
        "72gJMaTFClPr90oA7bkRYdUy0PJIcKQ8tj8bQvtP",
        env="PARSE_REST_API_KEY",
    )
    SYNC_YEAR_MIN: int = Field(2012, env="SYNC_YEAR_MIN")
    SYNC_YEAR_MAX: int = Field(2022, env="SYNC_YEAR_MAX")

    # Celery
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    CELERY_SYNC_HOUR: int = Field(0, env="CELERY_SYNC_HOUR")
    CELERY_SYNC_MINUTE: int = Field(0, env="CELERY_SYNC_MINUTE")
    CELERY_CONCURRENCY: int = Field(1, env="CELERY_CONCURRENCY")
    CELERY_LOG_LEVEL: str = Field("info", env="CELERY_LOG_LEVEL")

    # SQLAlchemy URIs
    SQLALCHEMY_DATABASE_URI: str = ""
    ASYNC_SQLALCHEMY_DATABASE_URI: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def model_post_init(self, __context=None):
        if self.ENV == "docker":
            self.POSTGRES_HOST = "db"
            self.REDIS_HOST = "redis"
            self.NEO4J_URI = "bolt://neo4j:7687"

        self.SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        self.ASYNC_SQLALCHEMY_DATABASE_URI = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

        self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        self.CELERY_RESULT_BACKEND = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


config = Config()
