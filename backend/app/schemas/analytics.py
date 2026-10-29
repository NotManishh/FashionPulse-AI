from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PlatformMetric(BaseModel):
    platform: str
    total_posts: int
    fashion_relevant_posts: int
    average_engagement: float
    last_collected_at: Optional[datetime] = None


class CategoryMetric(BaseModel):
    category: str
    trend_count: int
    total_mentions: int
    average_score: float


class AnalyticsOverviewResponse(BaseModel):
    total_collected_records: int
    total_active_trends: int
    active_connectors_count: int
    last_collection_time: Optional[datetime] = None
    latest_update_timestamp: datetime
    is_demo_mode: bool
    data_mode: str = "demo"  # live_youtube, full_live, partial_live, demo
    live_records_count: int = 0
    demo_records_count: int = 0
    platform_distribution: Dict[str, int]
    platform_live_distribution: Dict[str, int] = Field(default_factory=dict)
    platform_demo_distribution: Dict[str, int] = Field(default_factory=dict)
    category_distribution: List[CategoryMetric]
    emerging_trends_count: int
    peaking_trends_count: int
    average_confidence_score: float


class PlatformAnalyticsResponse(BaseModel):
    platforms: List[PlatformMetric]
