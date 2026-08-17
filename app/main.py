from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers.cars_routes import router as cars_router
from app.routers.users_routes import router as users_router
from app.routers.auth_routes import router as auth_router
from app.routers.reports_routes import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown tasks."""
    yield


app = FastAPI(title="Car App API", lifespan=lifespan)

app.include_router(cars_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(reports_router)

@app.get("/", tags=["Health"])
async def root():
    return {"message": "Welcome to Car App API!"}

