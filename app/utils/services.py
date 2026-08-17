from typing import Optional, Dict
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, and_, func

from app.models.car_model import Car, CarModel, Make

# -------------------- ASYNC FUNCTIONS (for FastAPI) -------------------- #

async def fetch_car_async(session: AsyncSession, car_id: int) -> Optional[Car]:
    result = await session.execute(
        select(Car)
        .where(Car.id == car_id)
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
    )
    return result.scalars().first()


async def get_user_car_async(session: AsyncSession, car_id: int, user_id: int) -> Car:
    car = await fetch_car_async(session, car_id)
    if not car or car.user_id != user_id:
        raise ValueError("Car not found or not owned by user")
    return car


async def get_or_create_make_async(session: AsyncSession, name: str) -> Make:
    make = (await session.execute(select(Make).where(Make.name == name))).scalars().first()
    if not make:
        make = Make(name=name)
        session.add(make)
        await session.flush()
    return make


async def get_or_create_model_async(session: AsyncSession, name: str, make_id: int) -> CarModel:
    car_model = (
        await session.execute(
            select(CarModel).where(and_(CarModel.name == name, CarModel.make_id == make_id))
        )
    ).scalars().first()
    if not car_model:
        car_model = CarModel(name=name, make_id=make_id)
        session.add(car_model)
        await session.flush()
    return car_model


async def create_car_with_model_async(
    session: AsyncSession,
    name: str,
    year: int,
    make_id: int,
    car_model_id: Optional[int] = None,
    car_model_name: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Car:
    if car_model_id:
        car_model = await session.get(CarModel, car_model_id)
        if not car_model:
            raise ValueError("CarModel with given ID not found")
    elif car_model_name:
        car_model = await get_or_create_model_async(session, car_model_name, make_id)
    else:
        raise ValueError("Either car_model_id or car_model_name must be provided")

    car = Car(
        car_model_id=car_model.id,
        name=name,
        year=year,
        category=category,
        user_id=user_id,
    )
    session.add(car)
    await session.flush()
    return car


async def update_car_data_async(
    session: AsyncSession,
    car: Car,
    data: Dict,
    car_model_name: Optional[str] = None,
    make_id: Optional[int] = None,
) -> Car:
    fields_to_update = ("name", "year", "category")
    for field in fields_to_update:
        if field in data:
            setattr(car, field, data[field])

    if car_model_name:
        car_model = await get_or_create_model_async(session, car_model_name, make_id)
        car.car_model_id = car_model.id

    await session.flush()
    return await fetch_car_async(session, car.id)


async def delete_car_async(session: AsyncSession, car: Car) -> None:
    await session.delete(car)
    await session.flush()


def build_car_reports_query(
    make: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):
    """
    Build a query for synced registration reports (Back4App data only).
    Supports filtering by make, model, year, and registration date range.
    """
    query = (
        select(Car)
        .join(Car.car_model)
        .join(CarModel.make)
        .where(Car.external_id.isnot(None))
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
    )

    if make:
        query = query.where(func.lower(Make.name).like(f"%{make.strip().lower()}%"))
    if model:
        query = query.where(func.lower(CarModel.name).like(f"%{model.strip().lower()}%"))
    if year is not None:
        query = query.where(Car.year == year)
    if date_from:
        query = query.where(Car.created_at >= date_from)
    if date_to:
        query = query.where(Car.created_at <= date_to)

    return query


def car_to_report_dict(car: Car) -> dict:
    """Map a Car ORM instance to a flat report response dict."""
    return {
        "id": car.id,
        "name": car.name,
        "year": car.year,
        "make": car.car_model.make.name if car.car_model and car.car_model.make else "",
        "model": car.car_model.name if car.car_model else "",
        "category": car.category,
        "created_at": car.created_at,
        "updated_at": car.updated_at,
    }


# -------------------- SYNC FUNCTIONS (for Celery) -------------------- #

def get_or_create_make_sync(session: Session, name: str) -> Make:
    make = session.query(Make).filter_by(name=name).first()
    if not make:
        make = Make(name=name)
        session.add(make)
        session.flush()
    return make


def get_or_create_model_sync(session: Session, name: str, make_id: int) -> CarModel:
    car_model = session.query(CarModel).filter_by(name=name, make_id=make_id).first()
    if not car_model:
        car_model = CarModel(name=name, make_id=make_id)
        session.add(car_model)
        session.flush()
    return car_model


def create_car_with_model_sync(
    session: Session,
    name: str,
    year: int,
    make_id: int,
    car_model_id: Optional[int] = None,
    car_model_name: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Car:
    if car_model_id:
        car_model = session.query(CarModel).get(car_model_id)
        if not car_model:
            raise ValueError("CarModel with given ID not found")
    elif car_model_name:
        car_model = get_or_create_model_sync(session, car_model_name, make_id)
    else:
        raise ValueError("Either car_model_id or car_model_name must be provided")

    car = Car(
        car_model_id=car_model.id,
        name=name,
        year=year,
        category=category,
        user_id=user_id,
    )
    session.add(car)
    session.flush()
    return car


def update_car_data_sync(
    session: Session,
    car: Car,
    data: Dict,
    car_model_name: Optional[str] = None,
    make_id: Optional[int] = None,
) -> Car:
    fields_to_update = ("name", "year", "category")
    for field in fields_to_update:
        if field in data:
            setattr(car, field, data[field])

    if car_model_name:
        car_model = get_or_create_model_sync(session, car_model_name, make_id)
        car.car_model_id = car_model.id

    session.flush()
    return car


def delete_car_sync(session: Session, car: Car) -> None:
    session.delete(car)
    session.flush()

