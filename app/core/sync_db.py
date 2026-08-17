from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from neo4j import GraphDatabase, Session as Neo4jSession

from app.core.config import config


# --- SQLAlchemy (PostgreSQL, sync) ---
engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a SQLAlchemy session for Celery tasks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Neo4j (sync) ---
neo4j_driver = GraphDatabase.driver(
    config.NEO4J_URI,
    auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
)


def get_neo4j_sync_session() -> Generator[Neo4jSession, None, None]:
    """
    Provide a Neo4j sync session for Celery tasks.
    """
    with neo4j_driver.session() as session:
        yield session

