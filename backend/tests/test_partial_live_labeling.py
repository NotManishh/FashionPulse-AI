import pytest
import httpx
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.entities import CollectedContent


@pytest.mark.asyncio
async def test_live_versus_demo_labeling(override_get_db, db_session: AsyncSession):
    """
    Verifies that when live records exist, the API endpoints accurately identify
    data_mode as partial_live (or full_live), and separate live vs demo counts.
    """
    # Seed 1 live YouTube record
    live_content = CollectedContent(
        platform="youtube",
        external_id="live_yt_test_123",
        title="Summer Minimalist Linen Capsule Wardrobe",
        content_text="Minimalist linen tailoring guide for summer fashion",
        author_id="test_fashion_creator",
        permalink="https://youtube.com/watch?v=live_yt_test_123",
        published_at=datetime.now(timezone.utc),
        raw_metrics={"views": 5000, "likes": 120, "comments": 45},
        normalized_engagement=1.5,
        is_fashion_related=True,
        is_demo=False
    )
    # Seed 1 demo record
    demo_content = CollectedContent(
        platform="reddit",
        external_id="demo_reddit_test_456",
        title="Demo Streetwear Guide",
        content_text="Oversized streetwear hoodie style guide",
        author_id="demo_user",
        permalink="https://reddit.com/r/streetwear/test",
        published_at=datetime.now(timezone.utc),
        raw_metrics={"upvotes": 100, "comments": 10},
        normalized_engagement=0.8,
        is_fashion_related=True,
        is_demo=True
    )
    db_session.add_all([live_content, demo_content])
    await db_session.commit()

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Test trends top 10
        trends_resp = await client.get("/api/v1/trends/top10")
        assert trends_resp.status_code == 200
        trends_data = trends_resp.json()
        assert trends_data["data_mode"] == "live_youtube"
        assert trends_data["is_demo_mode"] is False
        assert trends_data["live_records_count"] >= 1
        assert trends_data["demo_records_count"] >= 1

        # Test analytics overview
        analytics_resp = await client.get("/api/v1/analytics/overview")
        assert analytics_resp.status_code == 200
        analytics_data = analytics_resp.json()
        assert analytics_data["data_mode"] == "live_youtube"
        assert analytics_data["is_demo_mode"] is False
        assert analytics_data["live_records_count"] >= 1
        assert "youtube" in analytics_data["platform_live_distribution"]
        assert analytics_data["platform_live_distribution"]["youtube"] >= 1
        assert "reddit" in analytics_data["platform_demo_distribution"]
        assert analytics_data["platform_demo_distribution"]["reddit"] >= 1

        # Test connectors status
        conn_resp = await client.get("/api/v1/connectors/status")
        assert conn_resp.status_code == 200
        conn_data = conn_resp.json()
        yt_conn = next(c for c in conn_data["connectors"] if c["platform"] == "youtube")
        assert yt_conn["has_live_data"] is True
        assert yt_conn["live_records_ingested"] >= 1


@pytest.mark.asyncio
async def test_pure_demo_labeling(override_get_db, db_session: AsyncSession):
    """
    Verifies that when only demo records exist, data_mode is 'demo' and is_demo_mode is True.
    """
    demo_content = CollectedContent(
        platform="reddit",
        external_id="demo_reddit_only",
        title="Demo Only Guide",
        content_text="Sample fashion trend text",
        author_id="demo_user",
        permalink="https://reddit.com/r/fashion/test",
        published_at=datetime.now(timezone.utc),
        raw_metrics={"upvotes": 50, "comments": 5},
        normalized_engagement=0.5,
        is_fashion_related=True,
        is_demo=True
    )
    db_session.add(demo_content)
    await db_session.commit()

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        trends_resp = await client.get("/api/v1/trends/top10")
        assert trends_resp.status_code == 200
        trends_data = trends_resp.json()
        assert trends_data["data_mode"] == "demo"
        assert trends_data["is_demo_mode"] is True
        assert trends_data["live_records_count"] == 0
        assert trends_data["demo_records_count"] >= 1
