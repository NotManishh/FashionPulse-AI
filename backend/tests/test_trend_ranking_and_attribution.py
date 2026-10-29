import pytest
import httpx
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.main import app
from app.models.entities import CollectedContent, Trend
from app.services.trend_service import trend_service


@pytest.mark.asyncio
async def test_platform_breakdown_exclusively_from_genuine_observations(override_get_db, db_session: AsyncSession):
    """
    1. Verifies platform breakdowns and evidence badges are generated EXCLUSIVELY
    from genuine observations supporting each trend.
    Never attributes demo records or unconfigured Reddit/Instagram to live trends.
    """
    now = datetime.now(timezone.utc)
    # Add genuine live YouTube observations mentioning "chunky sneakers" and "baggy jeans"
    yt_obs_1 = CollectedContent(
        platform="youtube",
        external_id="yt_live_sneak_1",
        title="Chunky sneakers lookbook 2026",
        content_text="Styling chunky sneakers with casual streetwear",
        author_id="yt_user_1",
        permalink="https://youtube.com/watch?v=yt_live_sneak_1",
        published_at=now - timedelta(hours=2),
        raw_metrics={"views": 8000, "likes": 500, "comments": 80},
        normalized_engagement=2.8,
        is_fashion_related=True,
        extracted_terms=["Chunky & Dad Sneakers", "Chunky Sneakers"],
        is_demo=False
    )
    yt_obs_2 = CollectedContent(
        platform="youtube",
        external_id="yt_live_sneak_2",
        title="Summer outfit ideas with baggy jeans",
        content_text="Wearing baggy jeans and relaxed fit denim",
        author_id="yt_user_2",
        permalink="https://youtube.com/watch?v=yt_live_sneak_2",
        published_at=now - timedelta(hours=3),
        raw_metrics={"views": 4000, "likes": 200, "comments": 30},
        normalized_engagement=1.9,
        is_fashion_related=True,
        extracted_terms=["Wide-Leg & Baggy Denim", "Baggy Jeans"],
        is_demo=False
    )
    # Also have an old demo record mentioning oversized hoodies with reddit platform
    demo_reddit = CollectedContent(
        platform="reddit",
        external_id="demo_reddit_hoodie",
        title="Oversized hoodie styling",
        content_text="Oversized hoodies in streetwear",
        author_id="demo_user",
        permalink="https://reddit.com/r/streetwear/comments/123",
        published_at=now - timedelta(days=2),
        raw_metrics={"upvotes": 50, "comments": 10},
        normalized_engagement=1.0,
        is_fashion_related=True,
        extracted_terms=["Oversized Hoodies & Sweats"],
        is_demo=True
    )
    db_session.add_all([yt_obs_1, yt_obs_2, demo_reddit])
    await db_session.commit()

    # Trigger detection
    top_trends = await trend_service.get_top_10_trends(db_session)
    assert len(top_trends) > 0

    for trend in top_trends:
        assert trend.is_demo is False
        # Platform breakdown must ONLY contain platforms with genuine observations for this trend
        for plat, count in trend.platform_breakdown.items():
            assert plat == "youtube", f"Unexpected platform {plat} found in live trend {trend.name}!"
            assert count > 0
        assert "reddit" not in trend.platform_breakdown
        assert "instagram" not in trend.platform_breakdown


@pytest.mark.asyncio
async def test_rank_ordering_and_tie_breakers(override_get_db, db_session: AsyncSession):
    """
    2. Verifies top 10 trends are sorted globally by computed trend score in descending order,
    using momentum and confidence as documented tie-breakers.
    3. Verifies unique sequential ranks from 1 to N with no duplicate ranks.
    """
    now = datetime.now(timezone.utc)
    # Create observations with different engagement/frequencies to produce distinct scores
    records = []
    # Trend A: Highest engagement -> highest score
    for i in range(5):
        records.append(CollectedContent(
            platform="youtube",
            external_id=f"yt_high_{i}",
            title="Chunky sneakers trend",
            content_text="Chunky sneakers styling review",
            author_id=f"creator_{i}",
            permalink=f"https://youtube.com/watch?v=yt_high_{i}",
            published_at=now - timedelta(hours=i + 1),
            raw_metrics={"views": 50000, "likes": 3000, "comments": 400},
            normalized_engagement=4.5,
            is_fashion_related=True,
            extracted_terms=["Chunky & Dad Sneakers", "Chunky Sneakers"],
            is_demo=False
        ))
    # Trend B: Moderate engagement
    for i in range(3):
        records.append(CollectedContent(
            platform="youtube",
            external_id=f"yt_med_{i}",
            title="Baggy jeans trend",
            content_text="Baggy jeans outfit review",
            author_id=f"creator_med_{i}",
            permalink=f"https://youtube.com/watch?v=yt_med_{i}",
            published_at=now - timedelta(hours=i + 5),
            raw_metrics={"views": 8000, "likes": 400, "comments": 50},
            normalized_engagement=2.2,
            is_fashion_related=True,
            extracted_terms=["Wide-Leg & Baggy Denim", "Baggy Jeans"],
            is_demo=False
        ))
    # Trend C: Low engagement
    records.append(CollectedContent(
        platform="youtube",
        external_id="yt_low_1",
        title="Oversized blazer minimalist",
        content_text="Oversized blazer styling",
        author_id="creator_low",
        permalink="https://youtube.com/watch?v=yt_low_1",
        published_at=now - timedelta(hours=10),
        raw_metrics={"views": 500, "likes": 20, "comments": 2},
        normalized_engagement=1.0,
        is_fashion_related=True,
        extracted_terms=["Oversized Blazer"],
        is_demo=False
    ))
    db_session.add_all(records)
    await db_session.commit()

    top_trends = await trend_service.get_top_10_trends(db_session)
    assert len(top_trends) >= 3

    # Check unique sequential ranks starting at 1
    ranks = [t.current_rank for t in top_trends]
    assert len(ranks) == len(set(ranks)), f"Duplicate ranks found: {ranks}"
    assert ranks == list(range(1, len(ranks) + 1)), f"Non-sequential ranks: {ranks}"

    # Verify descending score order
    for idx in range(len(top_trends) - 1):
        curr_t = top_trends[idx]
        next_t = top_trends[idx + 1]
        if curr_t.current_score == next_t.current_score:
            # Tie breaker: momentum desc
            if curr_t.momentum_score == next_t.momentum_score:
                # Tie breaker: confidence desc
                assert curr_t.confidence >= next_t.confidence
            else:
                assert curr_t.momentum_score >= next_t.momentum_score
        else:
            assert curr_t.current_score > next_t.current_score, (
                f"Rank #{curr_t.current_rank} ({curr_t.name}, score {curr_t.current_score}) "
                f"has lower score than Rank #{next_t.current_rank} ({next_t.name}, score {next_t.current_score})"
            )


@pytest.mark.asyncio
async def test_old_demo_trends_unranked_when_live_active(override_get_db, db_session: AsyncSession):
    """
    Verifies that old demo trends from previous runs do not linger in the Top 10
    once live observations are ingested.
    """
    now = datetime.now(timezone.utc)
    # Seed an old demo trend directly into the trends table with rank 1
    demo_trend = Trend(
        id="demo_trend_old_hoodie",
        name="Oversized Hoodies & Sweats",
        category="Silhouettes & Tops",
        current_rank=1,
        current_score=95.0,
        confidence=0.8,
        momentum_score=90.0,
        mention_count=10,
        total_engagement=25.0,
        platform_breakdown={"reddit": 5, "instagram": 5},
        is_active=True,
        is_demo=True,
        first_seen=now - timedelta(days=5),
        last_seen=now - timedelta(days=2),
        updated_at=now - timedelta(days=2)
    )
    # Add a live YouTube record for "chunky sneakers"
    live_yt = CollectedContent(
        platform="youtube",
        external_id="yt_live_sneak_test",
        title="Chunky sneakers styling",
        content_text="Chunky sneakers fashion guide",
        author_id="creator_live",
        permalink="https://youtube.com/watch?v=yt_live_sneak_test",
        published_at=now - timedelta(hours=1),
        raw_metrics={"views": 5000, "likes": 300, "comments": 40},
        normalized_engagement=2.5,
        is_fashion_related=True,
        extracted_terms=["Chunky & Dad Sneakers", "Chunky Sneakers"],
        is_demo=False
    )
    db_session.add_all([demo_trend, live_yt])
    await db_session.commit()

    # Query top 10 trends
    top_trends = await trend_service.get_top_10_trends(db_session)
    
    # Old demo trend MUST NOT be in the top 10
    top_names = [t.name for t in top_trends]
    assert "Oversized Hoodies & Sweats" not in top_names
    for t in top_trends:
        assert t.is_demo is False
        assert "reddit" not in t.platform_breakdown
        assert "instagram" not in t.platform_breakdown

    # In DB, verify demo_trend has current_rank = None
    res = await db_session.execute(select(Trend).where(Trend.id == "demo_trend_old_hoodie"))
    updated_demo_trend = res.scalar_one()
    assert updated_demo_trend.current_rank is None


@pytest.mark.asyncio
async def test_nemotron_payload_source_platforms_and_data_mode(override_get_db, db_session: AsyncSession):
    """
    Verifies that Nemotron payload preview distinguishes live records from demo records,
    and reports source_platforms accurately reflecting genuine observations.
    """
    now = datetime.now(timezone.utc)
    live_yt = CollectedContent(
        platform="youtube",
        external_id="yt_nemotron_test",
        title="Baggy jeans lookbook",
        content_text="Styling baggy jeans for 2026",
        author_id="creator_nemotron",
        permalink="https://youtube.com/watch?v=yt_nemotron_test",
        published_at=now - timedelta(hours=1),
        raw_metrics={"views": 6000, "likes": 400, "comments": 50},
        normalized_engagement=2.6,
        is_fashion_related=True,
        extracted_terms=["Wide-Leg & Baggy Denim", "Baggy Jeans"],
        is_demo=False
    )
    db_session.add(live_yt)
    await db_session.commit()

    payload = await trend_service.build_nemotron_payload(db_session)
    assert payload.data_mode == "live_youtube"
    assert payload.source_platforms == ["youtube"]
    assert payload.live_observations_count >= 1
    for t in payload.trends:
        assert t.is_demo is False
        assert "reddit" not in t.platform_breakdown
        assert "instagram" not in t.platform_breakdown
