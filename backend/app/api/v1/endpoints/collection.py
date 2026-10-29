from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.collection_service import collection_service
from app.services.trend_service import trend_service
from app.schemas.content import CollectionTriggerRequest, CollectionJobResponse

router = APIRouter(prefix="/collection", tags=["Data Collection"])


@router.post("/run", response_model=CollectionJobResponse)
async def trigger_collection(
    request: CollectionTriggerRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers an on-demand data collection job across enabled platforms.
    Deduplicates records, classifies fashion content, extracts entities,
    and automatically recalculates the top 10 trends.
    """
    valid_platforms = ["all", "reddit", "instagram", "youtube"]
    plat = (request.platform or "all").lower()
    if plat not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform '{request.platform}'. Must be one of: {', '.join(valid_platforms)}"
        )

    # 1. Run collection ingestion
    job = await collection_service.run_collection(
        db=db,
        platform_filter=plat,
        trigger_type="manual",
        allow_demo_fallback=request.allow_demo_fallback
    )

    # 2. Recalculate trends with freshly ingested observations
    try:
        await trend_service.detect_and_update_trends(db=db)
    except Exception as ex:
        # Don't fail the collection job response if trend recalculation had non-fatal error
        pass

    return CollectionJobResponse(
        job_id=job.id,
        platform=job.platform,
        status=job.status,
        records_collected=job.records_collected,
        records_new=job.records_new,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        is_demo=job.is_demo
    )
