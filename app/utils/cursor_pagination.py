from typing import Generic, List, TypeVar, Optional, Type, Callable
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

T = TypeVar("T", bound=BaseModel)


class CursorPage(BaseModel, Generic[T]):
    """Generic schema for cursor-based pagination."""
    total: int
    items: List[T]
    next_cursor: Optional[int] = None


async def cursor_paginate(
    query,
    session: AsyncSession,
    schema: Type[T],
    model_id_field: str = "id",
    limit: int = 10,
    cursor: Optional[int] = None,
    item_mapper: Optional[Callable] = None,
) -> CursorPage[T]:
    """
    Cursor-based pagination helper.

    Applies optional cursor filter, returns a page of validated schema items,
    and counts total rows matching the base query filters.
    """
    model = query.column_descriptions[0]["entity"]
    id_column = getattr(model, model_id_field)

    filtered_query = query
    if cursor:
        filtered_query = filtered_query.where(id_column > cursor)

    result = await session.execute(
        filtered_query.order_by(id_column).limit(limit)
    )
    rows = result.scalars().all()

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    next_cursor = getattr(rows[-1], model_id_field) if rows else None

    if item_mapper:
        items = [schema.model_validate(item_mapper(row)) for row in rows]
    else:
        items = [schema.model_validate(row) for row in rows]

    return CursorPage[T](
        total=total,
        items=items,
        next_cursor=next_cursor,
    )
