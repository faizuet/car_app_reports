from functools import wraps
from asyncio import sleep
from typing import Callable, Any, Coroutine, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from app.models.car_model import Car, CarModel, Make


def db_commit_retry(retries: int = 3, delay: float = 0.5):
    """
    Decorator for async DB operations with commit retry.
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    result = await func(*args, **kwargs)
                    session: Optional[AsyncSession] = kwargs.get("session") or next(
                        (a for a in args if isinstance(a, AsyncSession)), None
                    )
                    if session:
                        await session.commit()
                    return result
                except SQLAlchemyError as e:
                    if attempt < retries - 1:
                        await sleep(delay)
                    else:
                        raise e
            return None
        return wrapper
    return decorator


async def fetch_car(session: AsyncSession, car_id: int) -> Optional[Car]:
    result = await session.execute(
        select(Car)
        .where(Car.id == car_id)
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
    )
    return result.scalars().first()


async def get_or_create_make(session: AsyncSession, name: str) -> Make:
    make = (await session.execute(select(Make).where(Make.name == name))).scalars().first()
    if not make:
        make = Make(name=name)
        session.add(make)
        await session.flush()
    return make


async def get_or_create_model(session: AsyncSession, name: str, make_id: int) -> CarModel:
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
    car_model = await session.get(CarModel, car_model_id)
    if not car_model:
        raise ValueError("CarModel not found")
    if name:
        car_model.name = name
    if make_id is not None:
        car_model.make_id = make_id
    await session.flush()

