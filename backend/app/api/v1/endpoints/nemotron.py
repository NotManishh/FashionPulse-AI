import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.database.session import get_db
from app.models.entities import NemotronHandoff
from app.services.trend_service import trend_service
from app.integrations.nemotron import nemotron_adapter
from app.schemas.nemotron import NemotronPayload, NemotronHandoffResponse

router = APIRouter(prefix="/nemotron", tags=["NVIDIA Nemotron Integration"])


@router.post("/preview", response_model=NemotronPayload)
async def preview_nemotron_payload(db: AsyncSession = Depends(get_db)):
    """
    Generates and previews the structured top-10 fashion trends payload
    formatted for the downstream NVIDIA Nemotron model.
    """
    payload = await trend_service.build_nemotron_payload(db)
    return payload


@router.post("/send", response_model=NemotronHandoffResponse)
async def send_to_nemotron(db: AsyncSession = Depends(get_db)):
    """
    Dispatches the top-10 trend payload to the configured NVIDIA Nemotron inference endpoint.
    If the endpoint is unconfigured, reports explicit error rather than simulating fake success.
    """
    payload = await trend_service.build_nemotron_payload(db)
    result = await nemotron_adapter.send_payload(payload)

    # Persist handoff attempt in database
    handoff_record = NemotronHandoff(
        id=result.handoff_id,
        payload=payload.model_dump(),
        status=result.status,
        response_status_code=result.status_code,
        response_body=result.response_summary,
        error_message=result.error_detail,
        timestamp=result.timestamp
    )
    db.add(handoff_record)
    await db.commit()

    return result
