from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.async_db import get_async_db
from app.deps.auth import get_current_user
from app.models.car_model import Car, CarModel
from app.schemas.car_schema import CarCreate, CarUpdate, CarRead
from app.utils.services import (
    update_car_model_fields,
    create_car_with_model,
    get_or_create_model,
)
from app.utils.cursor_pagination import cursor_paginate, CursorPage


router = APIRouter(prefix="/cars", tags=["Cars"])


async def get_car_with_relations(session: AsyncSession, car_id: int) -> Optional[Car]:
    """Fetch a car by ID, including its model and make."""
    result = await session.execute(
        select(Car)
        .where(Car.id == car_id)
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
    )
    return result.scalars().first()


async def get_user_car(session: AsyncSession, car_id: int, user_id: int) -> Car:
    """Ensure a car belongs to the given user, or raise 404."""
    car = await get_car_with_relations(session, car_id)
    if not car or car.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    return car


async def update_car_data(
    session: AsyncSession,
    car: Car,
    data: dict,
    car_model_name: Optional[str] = None,
    make_id: Optional[int] = None,
) -> Car:
    """Update a car’s attributes and model info."""
    # Update related CarModel if name or make changed
    if data.get("name") or data.get("make_id"):
        await update_car_model_fields(
            session,
            car.car_model_id,
            name=data.get("name"),
            make_id=data.get("make_id"),
        )

    # Update car fields
    if data.get("year"):
        car.year = data["year"]
    if data.get("category"):
        car.category = data["category"]

    # Update or create CarModel if a new name is provided
    if car_model_name:
        car_model = await get_or_create_model(session, name=car_model_name, make_id=make_id)
        car.car_model_id = car_model.id

    await session.commit()
    return await get_car_with_relations(session, car.id)


@router.post("/", response_model=CarRead, status_code=status.HTTP_201_CREATED)
async def create_car(
    payload: CarCreate,
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
) -> Car:
    """Create a new car for the current user."""
    try:
        car = await create_car_with_model(
            session=session,
            car_model_id=payload.car_model_id,
            car_model_name=payload.car_model_name,
            name=payload.name,
            year=payload.year,
            make_id=payload.make_id,
            user_id=int(current_user["sub"]),
            category=payload.category,
        )
        return await get_car_with_relations(session, car.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=CursorPage[CarRead])
async def list_cars(
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    cursor: Optional[int] = None,
) -> CursorPage[CarRead]:
    """List cars belonging to the current user with cursor pagination."""
    query = (
        select(Car)
        .where(Car.user_id == int(current_user["sub"]))
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
        .order_by(Car.id)
    )
    return await cursor_paginate(query, session, model_id_field="id", limit=limit, cursor=cursor)


@router.get("/{car_id}", response_model=CarRead)
async def get_car(
    car_id: int,
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
) -> Car:
    """Fetch a single car by ID if owned by the current user."""
    return await get_user_car(session, car_id, int(current_user["sub"]))


@router.patch("/{car_id}", response_model=CarRead)
async def patch_car(
    car_id: int,
    payload: CarUpdate,
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
) -> Car:
    """Partially update a car’s fields."""
    car = await get_user_car(session, car_id, int(current_user["sub"]))
    update_data = payload.dict(exclude_unset=True)
    return await update_car_data(session, car, update_data)


@router.put("/{car_id}", response_model=CarRead)
async def put_car(
    car_id: int,
    payload: CarCreate,
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
) -> Car:
    """Replace a car’s details entirely."""
    car = await get_user_car(session, car_id, int(current_user["sub"]))

    update_data = {
        "name": payload.name,
        "year": payload.year,
        "category": payload.category,
        "make_id": payload.make_id,
    }

    car_model_name = payload.car_model_name
    if payload.car_model_id:
        car_model = await session.get(CarModel, payload.car_model_id)
        if not car_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CarModel not found")
        car.car_model_id = car_model.id
        car_model_name = None

    return await update_car_data(
        session, car, update_data, car_model_name=car_model_name, make_id=payload.make_id
    )


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: int,
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
) -> None:
    """Delete a car belonging to the current user."""
    car = await get_user_car(session, car_id, int(current_user["sub"]))
    await session.delete(car)
    await session.commit()

