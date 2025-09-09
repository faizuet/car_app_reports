from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.car_model import Car, CarModel, Make


async def fetch_car(session: AsyncSession, car_id: int) -> Optional[Car]:
    """Fetch car with relations."""
    result = await session.execute(
        select(Car)
        .where(Car.id == car_id)
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
    )
    return result.scalars().first()


async def get_user_car(session: AsyncSession, car_id: int, user_id: int) -> Car:
    """Ensure car belongs to the given user."""
    car = await fetch_car(session, car_id)
    if not car or car.user_id != user_id:
        raise ValueError("Car not found or not owned by user")
    return car


async def get_or_create_make(session: AsyncSession, name: str) -> Make:
    """Find or create a Make."""
    make = (await session.execute(select(Make).where(Make.name == name))).scalars().first()
    if not make:
        make = Make(name=name)
        session.add(make)
        await session.flush()
    return make


async def get_or_create_model(session: AsyncSession, name: str, make_id: int) -> CarModel:
    """Find or create a CarModel."""
    car_model = (await session.execute(
        select(CarModel).where(and_(CarModel.name == name, CarModel.make_id == make_id))
    )).scalars().first()
    if not car_model:
        car_model = CarModel(name=name, make_id=make_id)
        session.add(car_model)
        await session.flush()
    return car_model


async def create_car_with_model(
    session: AsyncSession,
    name: str,
    year: int,
    make_id: int,
    car_model_id: Optional[int] = None,
    car_model_name: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None
) -> Car:
    """Create a Car linked to a CarModel (by id or name)."""
    if car_model_id:
        car_model = await session.get(CarModel, car_model_id)
        if not car_model:
            raise ValueError("CarModel with given ID not found")
    elif car_model_name:
        car_model = await get_or_create_model(session, car_model_name, make_id)
    else:
        raise ValueError("Either car_model_id or car_model_name must be provided")

    car = Car(
        car_model_id=car_model.id,
        name=name,
        year=year,
        category=category,
        user_id=user_id
    )
    session.add(car)
    await session.flush()
    return car


async def update_car_model_fields(
    session: AsyncSession,
    car_model_id: int,
    name: Optional[str] = None,
    make_id: Optional[int] = None,
):
    """Update CarModel fields."""
    car_model = await session.get(CarModel, car_model_id)
    if not car_model:
        raise ValueError("CarModel not found")
    if name:
        car_model.name = name
    if make_id is not None:
        car_model.make_id = make_id
    await session.flush()


async def update_car_data(
    session: AsyncSession,
    car: Car,
    data: dict,
    car_model_name: Optional[str] = None,
    make_id: Optional[int] = None,
) -> Car:
    """Update Car and its CarModel info."""
    if data.get("name") or data.get("make_id"):
        await update_car_model_fields(
            session,
            car.car_model_id,
            name=data.get("name"),
            make_id=data.get("make_id"),
        )

    if data.get("year"):
        car.year = data["year"]
    if data.get("category"):
        car.category = data["category"]

    if car_model_name:
        car_model = await get_or_create_model(session, name=car_model_name, make_id=make_id)
        car.car_model_id = car_model.id

    await session.flush()
    return await fetch_car(session, car.id)


async def delete_car(session: AsyncSession, car: Car) -> None:
    """Delete a car."""
    await session.delete(car)
    await session.flush()

