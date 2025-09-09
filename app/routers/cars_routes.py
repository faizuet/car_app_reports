from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.async_db import get_async_db
from app.deps.auth import get_current_user
from app.schemas.car_schema import CarCreate, CarUpdate, CarRead
from app.utils.cursor_pagination import cursor_paginate, CursorPage
from app.services.car_service import (
    fetch_car,
    get_user_car,
    create_car_with_model,
    update_car_data,
    delete_car,
)
from app.models.car_model import Car, CarModel

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post("/", response_model=CarRead, status_code=status.HTTP_201_CREATED)
async def create_car(
    payload: CarCreate,
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
):
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
        await session.commit()
        return await fetch_car(session, car.id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get("/", response_model=CursorPage[CarRead])
async def list_cars(
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    cursor: Optional[int] = None,
):
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
):
    try:
        return await get_user_car(session, car_id, int(current_user["sub"]))
    except ValueError:
        raise HTTPException(404, detail="Car not found")


@router.patch("/{car_id}", response_model=CarRead)
async def patch_car(
    car_id: int,
    payload: CarUpdate,
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
):
    try:
        car = await get_user_car(session, car_id, int(current_user["sub"]))
        update_data = payload.dict(exclude_unset=True)
        car = await update_car_data(session, car, update_data)
        await session.commit()
        return car
    except ValueError as e:
        raise HTTPException(404, detail=str(e))


@router.put("/{car_id}", response_model=CarRead)
async def put_car(
    car_id: int,
    payload: CarCreate,
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
):
    try:
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
                raise HTTPException(404, detail="CarModel not found")
            car.car_model_id = car_model.id
            car_model_name = None

        car = await update_car_data(session, car, update_data, car_model_name, payload.make_id)
        await session.commit()
        return car
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car_endpoint(
    car_id: int,
    session: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: dict = Depends(get_current_user),
):
    try:
        car = await get_user_car(session, car_id, int(current_user["sub"]))
        await delete_car(session, car)
        await session.commit()
    except ValueError:
        raise HTTPException(404, detail="Car not found")

