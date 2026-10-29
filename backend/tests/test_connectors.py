import pytest
from app.connectors.reddit import reddit_connector
from app.connectors.instagram import instagram_connector
from app.connectors.youtube import youtube_connector
from app.core.config import settings


def test_reddit_normalization():
    # Test RFR BigQuery Analytics Hub approved dataset record schema
    raw_rfr_record = {
        "id": "abc1234",
        "name": "t3_abc1234",
        "title": "Autumn street style with wide-leg jeans",
        "selftext": "Pairing baggy denim with cropped blazers.",
        "author": "rfr_masked_user_891",
        "subreddit": "streetwear",
        "permalink": "/r/streetwear/comments/abc1234",
        "score": 350,
        "upvote_ratio": 0.95,
        "num_comments": 42,
        "created_utc": 1700000000
    }
    norm = reddit_connector._normalize_rfr_record(raw_rfr_record)
    assert norm is not None
    assert norm.platform == "reddit"
    assert norm.external_id == "reddit_abc1234"
    assert "Autumn street style" in norm.title
    assert norm.author_id == "rfr_masked_user_891"
    assert norm.raw_metrics["score"] == 350
    assert norm.raw_metrics["upvote_ratio"] == 0.95
    assert norm.raw_metrics["num_comments"] == 42
    # Verify backward-compatible alias also works
    assert reddit_connector._normalize_reddit_post(raw_rfr_record) is not None


def test_instagram_normalization():
    raw_media = {
        "id": "media999",
        "caption": "Weekend quiet luxury #ootd #fashiontrends",
        "permalink": "https://instagram.com/p/media999",
        "timestamp": "2026-10-28T12:00:00+00:00",
        "like_count": 1500,
        "comments_count": 65
    }
    norm = instagram_connector._normalize_media_item(raw_media)
    assert norm is not None
    assert norm.platform == "instagram"
    assert norm.external_id == "ig_media999"
    assert norm.raw_metrics["like_count"] == 1500


def test_youtube_normalization():
    raw_video = {
        "id": "vid789",
        "snippet": {
            "title": "Top Fashion Trends 2026",
            "description": "Full guide to oversized hoodies and streetwear.",
            "channelTitle": "FashionChannel",
            "publishedAt": "2026-10-28T12:00:00Z"
        },
        "statistics": {
            "viewCount": "45000",
            "likeCount": "2200",
            "commentCount": "180"
        }
    }
    norm = youtube_connector._normalize_youtube_video(raw_video)
    assert norm is not None
    assert norm.platform == "youtube"
    assert norm.external_id == "yt_vid789"
    assert norm.raw_metrics["views"] == 45000


@pytest.mark.asyncio
async def test_demo_fallback_when_unconfigured(monkeypatch):
    # When credentials are not provided, connectors fetch labelled demo data
    monkeypatch.setattr(settings, "YOUTUBE_API_KEY", None)
    items = await reddit_connector.fetch_recent_content()
    assert len(items) > 0
    assert all(i.is_demo is True for i in items)

    ig_items = await instagram_connector.fetch_recent_content()
    assert len(ig_items) > 0
    assert all(i.is_demo is True for i in ig_items)

    yt_items = await youtube_connector.fetch_recent_content()
    assert len(yt_items) > 0
    assert all(i.is_demo is True for i in yt_items)


def test_instagram_api_version_is_current():
    # Meta Graph API v19.0 expired May 21, 2026; version must be v26.0 (latest supported)
    assert instagram_connector.api_version == "v26.0"
    assert "v19.0" not in instagram_connector.base_url
    assert "v21.0" not in instagram_connector.base_url
    assert "v26.0" in instagram_connector.base_url


def test_reddit_collector_disabled_by_default():
    # Reddit live collection must be disabled by default pending Reddit for Researchers (RFR) authorization
    assert reddit_connector.is_enabled is False
    assert reddit_connector.validate_credentials() is False
    missing = reddit_connector.get_missing_onboarding_details()
    assert any("ENABLE_REDDIT_RFR_INGESTION" in m for m in missing)
    assert any("RFR_GCP_PROJECT_ID" in m for m in missing)
    assert any("RFR_DATASET_NAME" in m for m in missing)


@pytest.mark.asyncio
async def test_unconfigured_authorization_fails_cleanly(monkeypatch):
    monkeypatch.setattr(settings, "YOUTUBE_API_KEY", None)
    assert await reddit_connector.verify_authorization() is False
    assert await instagram_connector.verify_authorization() is False
    assert await youtube_connector.verify_authorization() is False


@pytest.mark.asyncio
async def test_configured_youtube_authorization_succeeds():
    # When YOUTUBE_API_KEY is configured in .env, verify_authorization succeeds
    if settings.YOUTUBE_API_KEY:
        assert youtube_connector.validate_credentials() is True
        auth = await youtube_connector.verify_authorization()
        assert auth is True
        assert youtube_connector.is_authorized is True
        status = youtube_connector.get_status()
        assert status.is_configured is True
        assert status.is_authorized is True
