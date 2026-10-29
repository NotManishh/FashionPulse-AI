import pytest
from sqlalchemy import select, func
from app.services.collection_service import collection_service
from app.services.trend_service import trend_service
from app.models.entities import CollectedContent, Trend, TrendObservation
from app.core.config import settings


@pytest.mark.asyncio
async def test_end_to_end_trend_pipeline(db_session, monkeypatch):
    monkeypatch.setattr(settings, "YOUTUBE_API_KEY", None)
    # 1. Run collection
    job = await collection_service.run_collection(
        db=db_session,
        platform_filter="all",
        trigger_type="manual",
        allow_demo_fallback=True
    )
    assert job.records_new > 0

    # Verify records stored in CollectedContent
    count_res = await db_session.execute(select(func.count(CollectedContent.id)))
    assert (count_res.scalar() or 0) > 0

    # 2. Test duplicate detection: run collection again with same demo data
    second_job = await collection_service.run_collection(
        db=db_session,
        platform_filter="all",
        trigger_type="manual",
        allow_demo_fallback=True
    )
    # Deduplication should prevent new records from inserting duplicates
    assert second_job.records_new == 0

    # 3. Detect and update trends
    top_trends = await trend_service.detect_and_update_trends(db=db_session, days_window=7)
    assert len(top_trends) > 0
    assert len(top_trends) <= 10

    # 4. Verify historical observations created
    first_trend = top_trends[0]
    observations = await trend_service.get_trend_history(db=db_session, trend_id=first_trend.id)
    assert len(observations) > 0
    assert observations[0].trend_score == first_trend.current_score

    # 5. Build Nemotron handoff payload
    payload = await trend_service.build_nemotron_payload(db=db_session)
    assert len(payload.trends) == len(top_trends)
    assert payload.trends[0].trend_name == first_trend.name
