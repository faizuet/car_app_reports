from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.async_db import get_async_db, get_neo4j_service, Neo4jService
from app.deps.auth import get_current_user
from app.schemas.car_schema import CarCreate, CarUpdate, CarRead
from app.utils.cursor_pagination import cursor_paginate, CursorPage
from app.utils.services import (
    fetch_car_async,
    get_user_car_async,
    create_car_with_model_async,
    update_car_data_async,
    delete_car_async,
)

#  Import the async versions
from app.utils.neo4j_service import (
    create_car_node_async,
    update_car_node_async,
    delete_car_node_async,
)

from app.models.car_model import Car, CarModel

# --- Dependency Aliases ---
DBSession = Annotated[AsyncSession, Depends(get_async_db)]
Neo4jDep = Annotated[Neo4jService, Depends(get_neo4j_service)]
CurrentUser = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post("/", response_model=CarRead, status_code=status.HTTP_201_CREATED)
async def create_car(
    payload: CarCreate,
    db: DBSession,
    neo4j: Neo4jDep,
    user: CurrentUser,
):
    """Create a new car in PostgreSQL and mirror in Neo4j."""
    try:
        car = await create_car_with_model_async(
            session=db,
            car_model_id=payload.car_model_id,
            car_model_name=payload.car_model_name,
            name=payload.name,
            year=payload.year,
            make_id=payload.make_id,
            user_id=int(user["sub"]),
            category=payload.category,
        )
        await db.commit()
        car_data = await fetch_car_async(db, car.id)

        # Neo4j
        await neo4j.write(
            create_car_node_async,
            car_id=car_data.id,
            name=car_data.name,
            year=car_data.year,
            category=car_data.category,
            make_id=payload.make_id,
            user_id=int(user["sub"]),
        )
        return car_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=CursorPage[CarRead])
async def list_cars(
    db: DBSession,
    user: CurrentUser,
    limit: int = 10,
    cursor: Optional[int] = None,
):
    """List cars owned by the current user with pagination."""
    query = (
        select(Car)
        .where(Car.user_id == int(user["sub"]))
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
        .order_by(Car.id)
    )
    return await cursor_paginate(
        query, db, schema=CarRead, limit=limit, cursor=cursor
    )


@router.get("/{car_id}", response_model=CarRead)
async def get_car(
    car_id: int,
    db: DBSession,
    user: CurrentUser,
):
    """Fetch a single car if owned by the user."""
    try:
        return await get_user_car_async(db, car_id, int(user["sub"]))
    except ValueError:
        raise HTTPException(status_code=404, detail="Car not found")


@router.patch("/{car_id}", response_model=CarRead)
async def patch_car(
    car_id: int,
    payload: CarUpdate,
    db: DBSession,
    neo4j: Neo4jDep,
    user: CurrentUser,
):
    """Partially update a car (only provided fields)."""
    update_data = payload.dict(exclude_unset=True)
    try:
        car = await get_user_car_async(db, car_id, int(user["sub"]))
        car = await update_car_data_async(db, car, update_data)
        await db.commit()

        # Neo4j
        if update_data:
            await neo4j.write(update_car_node_async, car_id=car.id, updates=update_data)

        return car
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{car_id}", response_model=CarRead)
async def put_car(
    car_id: int,
    payload: CarCreate,
    db: DBSession,
    neo4j: Neo4jDep,
    user: CurrentUser,
):
    """Replace a car with new data (PUT)."""
    update_data = {
        "name": payload.name,
        "year": payload.year,
        "category": payload.category,
        "make_id": payload.make_id,
    }

    car_model_name = payload.car_model_name
    if payload.car_model_id:
        car_model = await db.get(CarModel, payload.car_model_id)
        if not car_model:
            raise HTTPException(status_code=404, detail="CarModel not found")
        car_model_name = None

    try:
        car = await get_user_car_async(db, car_id, int(user["sub"]))
        car = await update_car_data_async(db, car, update_data, car_model_name, payload.make_id)
        await db.commit()

        # Neo4j
        if update_data:
            await neo4j.write(update_car_node_async, car_id=car.id, updates=update_data)

        return car
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car_route(
    car_id: int,
    db: DBSession,
    neo4j: Neo4jDep,
    user: CurrentUser,
):
    """Delete a car from PostgreSQL and Neo4j."""
    try:
        car = await get_user_car_async(db, car_id, int(user["sub"]))
        await delete_car_async(db, car)
        await db.commit()

        # Neo4j
        await neo4j.write(delete_car_node_async, car_id=car.id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Car not found")

