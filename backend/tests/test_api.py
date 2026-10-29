import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint(override_get_db):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "FashionPulse" in data["service"]


@pytest.mark.asyncio
async def test_connectors_status_endpoint(override_get_db):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/connectors/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "connectors" in data
        assert len(data["connectors"]) == 3
        platforms = [c["platform"] for c in data["connectors"]]
        assert "reddit" in platforms
        assert "instagram" in platforms
        assert "youtube" in platforms


@pytest.mark.asyncio
async def test_collection_trigger_and_top10_flow(override_get_db):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Trigger collection with demo fallback
        trigger_resp = await client.post(
            "/api/v1/collection/run",
            json={"platform": "all", "allow_demo_fallback": True}
        )
        assert trigger_resp.status_code == 200
        job = trigger_resp.json()
        assert job["records_collected"] > 0
        assert job["status"] in ["completed", "partial"]

        # Fetch top 10 trends
        top10_resp = await client.get("/api/v1/trends/top10")
        assert top10_resp.status_code == 200
        top10_data = top10_resp.json()
        assert "trends" in top10_data
        assert len(top10_data["trends"]) > 0
        # Check ranks
        assert top10_data["trends"][0]["current_rank"] == 1


@pytest.mark.asyncio
async def test_analytics_overview_endpoint(override_get_db):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/analytics/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_collected_records" in data
        assert "platform_distribution" in data


@pytest.mark.asyncio
async def test_nemotron_preview_endpoint(override_get_db):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/nemotron/preview")
        assert resp.status_code == 200
        data = resp.json()
        assert "source_platforms" in data
        assert "trends" in data
