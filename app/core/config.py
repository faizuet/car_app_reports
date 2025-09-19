from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    # Project
    PROJECT_NAME: str = Field("Car App Reports", env="PROJECT_NAME")
    ENV: str = Field("local", env="ENV")  # local | docker

    # MySQL
    MYSQL_USER: str = Field("appuser", env="MYSQL_USER")
    MYSQL_PASSWORD: str = Field("AppPass123", env="MYSQL_PASSWORD")
    MYSQL_DB: str = Field("car_app_db", env="MYSQL_DB")
    MYSQL_HOST: str = Field("localhost", env="MYSQL_HOST")
    MYSQL_PORT: int = Field(3306, env="MYSQL_PORT")

    # Neo4j
    NEO4J_URI: str = Field("bolt://localhost:7687", env="NEO4J_URI")
    NEO4J_USER: str = Field("neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field("Neo4j_1234", env="NEO4J_PASSWORD")

    # Redis
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")

    # JWT / Auth
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")

    # Celery
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    CELERY_SYNC_INTERVAL: int = Field(5, env="CELERY_SYNC_INTERVAL")
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
        # Switch automatically between local and docker
        if self.ENV == "docker":
            self.MYSQL_HOST = "db"
            self.REDIS_HOST = "redis"
            self.NEO4J_URI = "bolt://neo4j:7687"

        # MySQL URIs
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

