from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ContentBase(BaseModel):
    platform: str
    external_id: str
    title: Optional[str] = None
    content_text: str
    author_id: Optional[str] = None
    permalink: Optional[str] = None
    published_at: datetime
    raw_metrics: Dict[str, Any] = Field(default_factory=dict)
    normalized_engagement: float = 0.0
    is_fashion_related: bool = True
    fashion_confidence: float = 1.0
    extracted_terms: List[str] = Field(default_factory=list)
    is_demo: bool = False


class ContentCreate(ContentBase):
    pass


class ContentResponse(ContentBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    collected_at: datetime


class CollectionTriggerRequest(BaseModel):
    platform: Optional[str] = Field(default="all", description="all, reddit, instagram, or youtube")
    force_refresh: bool = Field(default=False)
    allow_demo_fallback: bool = Field(default=True, description="Use labelled demo data if credentials not configured")


class CollectionJobResponse(BaseModel):
    job_id: str
    platform: str
    status: str
    records_collected: int
    records_new: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    is_demo: bool
