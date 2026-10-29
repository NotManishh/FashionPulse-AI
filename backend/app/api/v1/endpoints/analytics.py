from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone
from typing import Dict, List
from app.database.session import get_db
from app.models.entities import CollectedContent, Trend, ConnectorStatus, CollectionJob
from app.schemas.analytics import AnalyticsOverviewResponse, PlatformAnalyticsResponse, PlatformMetric, CategoryMetric

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    """Overview statistics for dashboard metrics and visualizations."""
    now = datetime.now(timezone.utc)

    # Total collected records
    total_records_res = await db.execute(select(func.count(CollectedContent.id)))
    total_records = total_records_res.scalar() or 0

    # Total active trends
    active_trends_res = await db.execute(
        select(func.count(Trend.id)).where(Trend.is_active == True)
    )
    total_trends = active_trends_res.scalar() or 0

    # Active connectors
    conn_res = await db.execute(
        select(func.count(ConnectorStatus.platform)).where(ConnectorStatus.is_configured == True)
    )
    active_connectors = conn_res.scalar() or 0

    # Last collection time
    last_job_res = await db.execute(
        select(CollectionJob.completed_at).where(CollectionJob.status.in_(["completed", "partial"])).order_by(CollectionJob.completed_at.desc()).limit(1)
    )
    last_collection_time = last_job_res.scalar_one_or_none()

    # Demo data check: Mode is demo if zero live records exist
    demo_count_res = await db.execute(
        select(func.count(CollectedContent.id)).where(CollectedContent.is_demo == True)
    )
    demo_records_count = demo_count_res.scalar() or 0

    live_count_res = await db.execute(
        select(func.count(CollectedContent.id)).where(CollectedContent.is_demo == False)
    )
    live_records_count = live_count_res.scalar() or 0

    # YouTube-only production data mode determination
    if live_records_count > 0:
        data_mode = "live_youtube"
        is_demo = False
    else:
        data_mode = "demo"
        is_demo = True

    # Platform total distribution
    plat_dist_res = await db.execute(
        select(CollectedContent.platform, func.count(CollectedContent.id)).group_by(CollectedContent.platform)
    )
    platform_distribution: Dict[str, int] = {row[0]: row[1] for row in plat_dist_res.all()}
    for p in ["reddit", "instagram", "youtube"]:
        platform_distribution.setdefault(p, 0)

    # Platform LIVE distribution
    plat_live_res = await db.execute(
        select(CollectedContent.platform, func.count(CollectedContent.id))
        .where(CollectedContent.is_demo == False)
        .group_by(CollectedContent.platform)
    )
    platform_live_distribution: Dict[str, int] = {row[0]: row[1] for row in plat_live_res.all()}
    for p in ["reddit", "instagram", "youtube"]:
        platform_live_distribution.setdefault(p, 0)

    # Platform DEMO distribution
    plat_demo_res = await db.execute(
        select(CollectedContent.platform, func.count(CollectedContent.id))
        .where(CollectedContent.is_demo == True)
        .group_by(CollectedContent.platform)
    )
    platform_demo_distribution: Dict[str, int] = {row[0]: row[1] for row in plat_demo_res.all()}
    for p in ["reddit", "instagram", "youtube"]:
        platform_demo_distribution.setdefault(p, 0)

    # Category distribution of trends
    cat_res = await db.execute(
        select(
            Trend.category,
            func.count(Trend.id),
            func.sum(Trend.mention_count),
            func.avg(Trend.current_score)
        ).where(Trend.is_active == True).group_by(Trend.category)
    )
    category_distribution: List[CategoryMetric] = []
    for row in cat_res.all():
        category_distribution.append(
            CategoryMetric(
                category=row[0] or "General",
                trend_count=row[1] or 0,
                total_mentions=int(row[2] or 0),
                average_score=round(float(row[3] or 0.0), 1)
            )
        )

    # Status counts
    emerging_res = await db.execute(
        select(func.count(Trend.id)).where(Trend.growth_status.in_(["emerging", "rising", "provisional"]))
    )
    emerging_count = emerging_res.scalar() or 0

    peaking_res = await db.execute(
        select(func.count(Trend.id)).where(Trend.growth_status == "peaking")
    )
    peaking_count = peaking_res.scalar() or 0

    avg_conf_res = await db.execute(select(func.avg(Trend.confidence)).where(Trend.is_active == True))
    avg_conf = float(avg_conf_res.scalar() or 0.85)

    return AnalyticsOverviewResponse(
        total_collected_records=total_records,
        total_active_trends=total_trends,
        active_connectors_count=active_connectors,
        last_collection_time=last_collection_time,
        latest_update_timestamp=now,
        is_demo_mode=is_demo,
        data_mode=data_mode,
        live_records_count=live_records_count,
        demo_records_count=demo_records_count,
        platform_distribution=platform_distribution,
        platform_live_distribution=platform_live_distribution,
        platform_demo_distribution=platform_demo_distribution,
        category_distribution=category_distribution,
        emerging_trends_count=emerging_count,
        peaking_trends_count=peaking_count,
        average_confidence_score=round(avg_conf, 2)
    )


@router.get("/platforms", response_model=PlatformAnalyticsResponse)
async def get_platform_analytics(db: AsyncSession = Depends(get_db)):
    """Returns platform-level ingestion statistics, fashion relevance ratio, and engagement averages."""
    platforms = ["reddit", "instagram", "youtube"]
    metrics: List[PlatformMetric] = []

    for plat in platforms:
        tot_res = await db.execute(
            select(func.count(CollectedContent.id)).where(CollectedContent.platform == plat)
        )
        total_posts = tot_res.scalar() or 0

        fash_res = await db.execute(
            select(func.count(CollectedContent.id)).where(
                and_(CollectedContent.platform == plat, CollectedContent.is_fashion_related == True)
            )
        )
        fashion_posts = fash_res.scalar() or 0

        eng_res = await db.execute(
            select(func.avg(CollectedContent.normalized_engagement)).where(CollectedContent.platform == plat)
        )
        avg_eng = float(eng_res.scalar() or 0.0)

        last_col_res = await db.execute(
            select(CollectedContent.collected_at).where(CollectedContent.platform == plat).order_by(CollectedContent.collected_at.desc()).limit(1)
        )
        last_time = last_col_res.scalar_one_or_none()

        metrics.append(
            PlatformMetric(
                platform=plat,
                total_posts=total_posts,
                fashion_relevant_posts=fashion_posts,
                average_engagement=round(avg_eng, 2),
                last_collected_at=last_time
            )
        )

    return PlatformAnalyticsResponse(platforms=metrics)
