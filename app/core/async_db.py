from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from neo4j import AsyncGraphDatabase

from app.core.config import config

# --- SQLAlchemy (PostgreSQL) ---
async_engine = create_async_engine(
    config.ASYNC_SQLALCHEMY_DATABASE_URI,
    echo=False,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# --- Neo4j (Async) ---
neo4j_async_driver = AsyncGraphDatabase.driver(
    config.NEO4J_URI,
    auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
)

class Neo4jService:
    """Wrapper around Neo4j driver for cleaner usage in routes."""

    def __init__(self, driver):
        self._driver = driver

    async def write(self, fn, **kwargs):
        async with self._driver.session() as session:
            return await session.execute_write(fn, **kwargs)

    async def read(self, fn, **kwargs):
        async with self._driver.session() as session:
            return await session.execute_read(fn, **kwargs)

# Dependency for FastAPI routes (Neo4j)
async def get_neo4j_service() -> Neo4jService:
    return Neo4jService(neo4j_async_driver)

