from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.database.session import get_db
from app.models.entities import ConnectorStatus, CollectedContent
from app.schemas.connector import AllConnectorsStatusResponse, ConnectorStatusResponse
from app.connectors.reddit import reddit_connector
from app.connectors.instagram import instagram_connector
from app.connectors.youtube import youtube_connector

router = APIRouter(prefix="/connectors", tags=["Connectors"])

CONNECTORS = {
    "reddit": reddit_connector,
    "instagram": instagram_connector,
    "youtube": youtube_connector
}


@router.get("/status", response_model=AllConnectorsStatusResponse)
async def get_all_connectors_status(
    audit: bool = Query(default=False, description="Run live authorization check on configured connectors"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves live authorization and configuration status for Reddit, Instagram, and YouTube."""
    result = await db.execute(select(ConnectorStatus))
    db_statuses = {row.platform: row for row in result.scalars().all()}
    
    response_items: List[ConnectorStatusResponse] = []
    active_count = 0

    for platform_name, connector in CONNECTORS.items():
        db_row = db_statuses.get(platform_name)
        is_configured = connector.validate_credentials()

        if is_configured:
            active_count += 1
            # Perform live API authorization check if requested or if not yet authorized
            if audit or not connector.is_authorized:
                await connector.verify_authorization()

        status_info = connector.get_status()

        # Query live (non-demo) records actually collected for this platform
        live_records_res = await db.execute(
            select(func.count(CollectedContent.id)).where(
                CollectedContent.platform == platform_name,
                CollectedContent.is_demo == False
            )
        )
        live_records_count = live_records_res.scalar_one_or_none() or 0
        has_live = live_records_count > 0

        # Query demo records for this platform
        demo_records_res = await db.execute(
            select(func.count(CollectedContent.id)).where(
                CollectedContent.platform == platform_name,
                CollectedContent.is_demo == True
            )
        )
        demo_records_count = demo_records_res.scalar_one_or_none() or 0

        # Sync runtime state back to DB record if present
        if db_row:
            db_row.is_configured = status_info.is_configured
            db_row.is_authorized = status_info.is_authorized
            if status_info.last_error_message:
                db_row.last_error_message = status_info.last_error_message
                db_row.last_error_at = status_info.last_error_at
            db_row.updated_at = datetime.now(timezone.utc)

        response_items.append(
            ConnectorStatusResponse(
                platform=platform_name,
                status_tier="production" if platform_name == "youtube" else "future_integration",
                is_configured=status_info.is_configured,
                is_authorized=status_info.is_authorized,
                has_live_data=has_live,
                live_records_ingested=live_records_count,
                demo_records_ingested=demo_records_count,
                last_success_at=db_row.last_success_at if db_row else status_info.last_success_at,
                last_error_at=db_row.last_error_at if db_row else status_info.last_error_at,
                last_error_message=db_row.last_error_message if db_row else status_info.last_error_message,
                total_records_ingested=live_records_count + demo_records_count,
                rate_limit_info=status_info.rate_limit_info,
                updated_at=db_row.updated_at if db_row else status_info.last_success_at or datetime.now()
            )
        )

    await db.commit()

    return AllConnectorsStatusResponse(
        connectors=response_items,
        active_count=active_count,
        all_configured=(active_count == len(CONNECTORS))
    )

