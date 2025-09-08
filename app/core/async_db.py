from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import config


# Async engine
async_engine = create_async_engine(
    config.ASYNC_SQLALCHEMY_DATABASE_URI,
    echo=False,
    future=True,
)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency for FastAPI routes
async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

