import pytest
from app.schemas.nemotron import NemotronPayload, NemotronTrendItem
from app.integrations.nemotron import MockNemotronAdapter, NemotronServiceAdapter


def test_nemotron_payload_structure():
    payload = NemotronPayload(
        generated_at="2026-10-28T12:00:00Z",
        time_window="7d",
        source_platforms=["reddit", "instagram", "youtube"],
        total_observations_analyzed=50,
        trends=[
            NemotronTrendItem(
                rank=1,
                trend_name="Wide-Leg & Baggy Denim",
                trend_score=85.5,
                confidence=0.92,
                momentum_score=78.0,
                mention_count=45,
                platform_breakdown={"reddit": 20, "instagram": 15, "youtube": 10},
                growth_rate=45.0,
                category="Pants & Denim",
                supporting_keywords=["baggy jeans", "loose fit denim"]
            )
        ]
    )
    dumped = payload.model_dump()
    assert dumped["time_window"] == "7d"
    assert len(dumped["trends"]) == 1
    assert dumped["trends"][0]["trend_score"] == 85.5


@pytest.mark.asyncio
async def test_mock_nemotron_adapter_success():
    adapter = MockNemotronAdapter(simulate_success=True)
    payload = NemotronPayload(
        generated_at="2026-10-28T12:00:00Z",
        time_window="7d",
        source_platforms=["reddit", "instagram", "youtube"],
        total_observations_analyzed=10,
        trends=[]
    )
    resp = await adapter.send_payload(payload)
    assert resp.status == "sent"
    assert resp.status_code == 200
    assert resp.error_detail is None


@pytest.mark.asyncio
async def test_mock_nemotron_adapter_failure():
    adapter = MockNemotronAdapter(simulate_success=False)
    payload = NemotronPayload(
        generated_at="2026-10-28T12:00:00Z",
        time_window="7d",
        source_platforms=["reddit", "instagram", "youtube"],
        total_observations_analyzed=10,
        trends=[]
    )
    resp = await adapter.send_payload(payload)
    assert resp.status == "failed"
    assert resp.status_code == 503
    assert resp.error_detail is not None


@pytest.mark.asyncio
async def test_unconfigured_service_adapter_aborts_safely():
    # Production adapter with empty endpoint should not pretend it was called
    service_adapter = NemotronServiceAdapter()
    service_adapter.endpoint_url = None
    payload = NemotronPayload(
        generated_at="2026-10-28T12:00:00Z",
        time_window="7d",
        source_platforms=["reddit", "instagram", "youtube"],
        total_observations_analyzed=10,
        trends=[]
    )
    resp = await service_adapter.send_payload(payload)
    assert resp.status == "failed"
    assert "Nemotron not configured" in resp.error_detail
