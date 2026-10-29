from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ConnectorStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    platform: str
    is_configured: bool
    is_authorized: bool
    has_live_data: bool = False
    live_records_ingested: int = 0
    demo_records_ingested: int = 0
    status_tier: str = "production"  # "production" or "future_integration"
    last_success_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    last_error_message: Optional[str] = None
    total_records_ingested: int
    rate_limit_info: Dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime


class AllConnectorsStatusResponse(BaseModel):
    connectors: List[ConnectorStatusResponse]
    active_count: int
    all_configured: bool
    primary_platform: str = "youtube"
