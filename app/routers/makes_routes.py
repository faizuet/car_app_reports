from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.async_db import get_async_db
from app.deps.auth import get_current_user
from app.models.car_model import Make, CarModel
from app.schemas.car_schema import MakeRead, CarModelRead

DBSession = Annotated[AsyncSession, Depends(get_async_db)]
CurrentUser = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="/makes", tags=["Makes"])


@router.get("/", response_model=List[MakeRead])
async def list_makes(db: DBSession, user: CurrentUser):
    """List all car makes from synced data."""
    result = await db.execute(select(Make).order_by(Make.name))
    return result.scalars().all()


@router.get("/{make_id}/models", response_model=List[CarModelRead])
async def list_models_for_make(make_id: int, db: DBSession, user: CurrentUser):
    """List car models for a given make."""
    make = await db.get(Make, make_id)
    if not make:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Make not found")

    result = await db.execute(
        select(CarModel)
        .where(CarModel.make_id == make_id)
        .options(selectinload(CarModel.make))
        .order_by(CarModel.name)
    )
    return result.scalars().all()
