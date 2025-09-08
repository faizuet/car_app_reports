from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers.cars_routes import router as cars_router
from app.routers.users_routes import router as users_router
from app.routers.auth_routes import router as auth_router
from app.core.async_db import async_engine
from app.core.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown tasks."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Car App API", lifespan=lifespan)

app.include_router(cars_router)
app.include_router(users_router)
app.include_router(auth_router)

@app.get("/", tags=["Health"])
async def root():
    return {"message": "Welcome to Car App API!"}

