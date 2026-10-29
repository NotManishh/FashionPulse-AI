from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TrendObservationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    observation_window_start: datetime
    observation_window_end: datetime
    mention_count: int
    engagement_score: float
    trend_score: float
    platform: str
    recorded_at: datetime


class TrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    category: str
    description: Optional[str] = None
    current_rank: Optional[int] = None
    current_score: float
    confidence: float
    momentum_score: float
    growth_rate: Optional[float] = None
    growth_status: str
    mention_count: int
    total_engagement: float
    platform_breakdown: Dict[str, int] = Field(default_factory=dict)
    first_seen: datetime
    last_seen: datetime
    time_window: str
    supporting_keywords: List[str] = Field(default_factory=list)
    representative_references: List[str] = Field(default_factory=list)
    is_active: bool
    is_demo: bool = False
    updated_at: datetime


class Top10TrendsResponse(BaseModel):
    generated_at: datetime
    time_window: str
    total_trends_found: int
    is_demo_mode: bool
    data_mode: str = "demo"  # live_youtube, full_live, partial_live, demo
    live_records_count: int = 0
    demo_records_count: int = 0
    trends: List[TrendResponse]


class TrendHistoryResponse(BaseModel):
    trend_id: str
    trend_name: str
    observations: List[TrendObservationSchema]
