from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime, timezone
from app.database.session import get_db
from app.models.entities import Trend, CollectedContent, ConnectorStatus
from app.services.trend_service import trend_service
from app.schemas.trend import TrendResponse, Top10TrendsResponse, TrendHistoryResponse, TrendObservationSchema

router = APIRouter(prefix="/trends", tags=["Fashion Trends"])


@router.get("/top10", response_model=Top10TrendsResponse)
async def get_top_10_trends(db: AsyncSession = Depends(get_db)):
    """
    Returns the definitive ranked Top 10 fashion trends derived dynamically
    from cross-platform social observations.
    """
    trends = await trend_service.get_top_10_trends(db)

    demo_count_res = await db.execute(
        select(func.count(CollectedContent.id)).where(CollectedContent.is_demo == True)
    )
    demo_records_count = demo_count_res.scalar() or 0

    live_count_res = await db.execute(
        select(func.count(CollectedContent.id)).where(CollectedContent.is_demo == False)
    )
    live_records_count = live_count_res.scalar() or 0

    conn_res = await db.execute(
        select(func.count(ConnectorStatus.platform)).where(
            ConnectorStatus.is_configured == True,
            ConnectorStatus.is_authorized == True
        )
    )
    authorized_conn_count = conn_res.scalar() or 0

    # YouTube-only production data mode determination
    if live_records_count > 0:
        data_mode = "live_youtube"
        is_demo = False
    else:
        data_mode = "demo"
        is_demo = True

    return Top10TrendsResponse(
        generated_at=datetime.now(timezone.utc),
        time_window="7d",
        total_trends_found=len(trends),
        is_demo_mode=is_demo,
        data_mode=data_mode,
        live_records_count=live_records_count,
        demo_records_count=demo_records_count,
        trends=[TrendResponse.model_validate(t) for t in trends]
    )


@router.get("", response_model=List[TrendResponse])
async def list_trends(
    category: Optional[str] = Query(None, description="Filter by fashion category"),
    search: Optional[str] = Query(None, description="Search by trend name or keyword"),
    status: Optional[str] = Query(None, description="Filter by status: rising, steady, peaking, emerging"),
    limit: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Lists fashion trends with optional category and search filters."""
    query = select(Trend).where(Trend.is_active == True)

    if category:
        query = query.where(Trend.category.ilike(f"%{category}%"))
    if status:
        query = query.where(Trend.growth_status == status)
    if search:
        query = query.where(Trend.name.ilike(f"%{search}%"))

    query = query.order_by(Trend.current_score.desc()).limit(limit)
    result = await db.execute(query)
    trends = result.scalars().all()
    return [TrendResponse.model_validate(t) for t in trends]


@router.get("/{trend_id}", response_model=TrendResponse)
async def get_trend_by_id(trend_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full details for a specific trend."""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    if not trend:
        raise HTTPException(status_code=404, detail=f"Trend '{trend_id}' not found.")
    return TrendResponse.model_validate(trend)


@router.get("/{trend_id}/history", response_model=TrendHistoryResponse)
async def get_trend_history(trend_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves time-series observation snapshots for tracking trend growth over time."""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    if not trend:
        raise HTTPException(status_code=404, detail=f"Trend '{trend_id}' not found.")

    observations = await trend_service.get_trend_history(db, trend_id)
    return TrendHistoryResponse(
        trend_id=trend.id,
        trend_name=trend.name,
        observations=[TrendObservationSchema.model_validate(o) for o in observations]
    )
