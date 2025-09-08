from typing import Generic, List, TypeVar, Optional, Type
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.schemas.car_schema import CarRead

T = TypeVar("T", bound=BaseModel)


class CursorPage(BaseModel, Generic[T]):
    """Generic schema for cursor-based pagination."""
    total: int
    items: List[T]
    next_cursor: Optional[int] = None


class CarCursorPage(CursorPage[CarRead]):
    """Cursor-based pagination specifically for Cars."""
    items: List[CarRead]


async def cursor_paginate(
    query,
    session: AsyncSession,
    schema: Type[T],  # NEW: pass schema here
    model_id_field: str = "id",
    limit: int = 10,
    cursor: Optional[int] = None,
) -> CursorPage[T]:
    """
    Cursor-based pagination helper.
    """
    model = query.column_descriptions[0]["entity"]
    id_column = getattr(model, model_id_field)

    # Apply cursor filter
    if cursor:
        query = query.where(id_column > cursor)

    # Fetch paginated items
    result = await session.execute(
        query.order_by(id_column).limit(limit)
    )
    items = result.scalars().all()

    # Count total records
    total_result = await session.execute(select(func.count(id_column)))
    total = total_result.scalar() or 0

    # Next cursor = last item’s ID
    next_cursor = getattr(items[-1], model_id_field) if items else None

    return CursorPage[T](
        total=total,
        items=[schema.from_orm(item) for item in items],
        next_cursor=next_cursor,
    )

