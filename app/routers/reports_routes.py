from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.async_db import get_async_db
from app.deps.auth import get_current_user
from app.schemas.car_schema import CarReportRead, CarSearchQuery
from app.utils.cursor_pagination import cursor_paginate, CursorPage
from app.utils.services import build_car_reports_query, car_to_report_dict

DBSession = Annotated[AsyncSession, Depends(get_async_db)]
CurrentUser = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/", response_model=CursorPage[CarReportRead])
async def search_reports(
    db: DBSession,
    user: CurrentUser,
    make: Optional[str] = Query(None, description="Filter by car make (partial match)"),
    model: Optional[str] = Query(None, description="Filter by car model (partial match)"),
    year: Optional[int] = Query(None, ge=2012, le=2022, description="Filter by manufacturing year"),
    date_from: Optional[datetime] = Query(None, description="Filter reports created on or after this date"),
    date_to: Optional[datetime] = Query(None, description="Filter reports created on or before this date"),
    limit: int = Query(10, ge=1, le=100),
    cursor: Optional[int] = Query(None, description="Pagination cursor (last seen car id)"),
):
    """
    Search car registration reports synced from Back4App.

    Authenticated users can filter by make, model, year, and registration date.
    Results are paginated using cursor-based pagination.
    """
    search = CarSearchQuery(
        make=make,
        model=model,
        year=year,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        cursor=cursor,
    )

    query = build_car_reports_query(
        make=search.make,
        model=search.model,
        year=search.year,
        date_from=search.date_from,
        date_to=search.date_to,
    )

    return await cursor_paginate(
        query,
        db,
        schema=CarReportRead,
        limit=search.limit,
        cursor=search.cursor,
        item_mapper=car_to_report_dict,
    )
