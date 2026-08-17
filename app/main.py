from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import config
from app.routers.cars_routes import router as cars_router
from app.routers.users_routes import router as users_router
from app.routers.auth_routes import router as auth_router
from app.routers.reports_routes import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown tasks."""
    Path(config.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Car App API", lifespan=lifespan)

origins = [origin.strip() for origin in config.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=config.UPLOAD_DIR), name="uploads")

app.include_router(cars_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(reports_router)

@app.get("/", tags=["Health"])
async def root():
    return {"message": "Welcome to Car App API!"}

