from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel


class NormalizedContentItem(BaseModel):
    platform: str
    external_id: str
    title: Optional[str] = None
    content_text: str
    author_id: Optional[str] = None
    permalink: Optional[str] = None
    published_at: datetime
    raw_metrics: Dict[str, Any]
    is_demo: bool = False


class ConnectorStatusInfo(BaseModel):
    platform: str
    is_configured: bool
    is_authorized: bool
    has_live_data: bool = False
    live_records_ingested: int = 0
    last_success_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    last_error_message: Optional[str] = None
    total_records_ingested: int = 0
    rate_limit_info: Dict[str, Any] = {}


class BaseSocialConnector(ABC):
    """Abstract base class for all social media platform connectors."""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.is_authorized: bool = False
        self.last_success_at: Optional[datetime] = None
        self.last_error_at: Optional[datetime] = None
        self.last_error_message: Optional[str] = None
        self.total_records_ingested: int = 0
        self.live_records_ingested: int = 0
        self.rate_limit_info: Dict[str, Any] = {}

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Checks if required API keys / tokens exist in configuration."""
        pass

    @abstractmethod
    async def verify_authorization(self) -> bool:
        """Makes a test call to verify live API authorization."""
        pass

    @abstractmethod
    async def fetch_recent_content(self, limit: int = 25) -> List[NormalizedContentItem]:
        """Fetches and returns normalized content from the platform."""
        pass

    def get_status(self) -> ConnectorStatusInfo:
        """Returns the current runtime status of this connector."""
        is_cfg = self.validate_credentials()
        # If credentials are not configured, connector cannot be authorized
        if not is_cfg:
            self.is_authorized = False
            
        return ConnectorStatusInfo(
            platform=self.platform_name,
            is_configured=is_cfg,
            is_authorized=bool(is_cfg and self.is_authorized),
            has_live_data=(self.live_records_ingested > 0),
            live_records_ingested=self.live_records_ingested,
            last_success_at=self.last_success_at,
            last_error_at=self.last_error_at,
            last_error_message=self.last_error_message,
            total_records_ingested=self.total_records_ingested,
            rate_limit_info=self.rate_limit_info
        )

    def record_success(self, count: int, is_demo: bool = False):
        self.last_success_at = datetime.now(timezone.utc)
        self.last_error_message = None
        self.total_records_ingested += count
        if not is_demo and count > 0:
            self.live_records_ingested += count
            self.is_authorized = True

    def record_error(self, message: str):
        self.last_error_at = datetime.now(timezone.utc)
        self.last_error_message = message
        self.is_authorized = False
