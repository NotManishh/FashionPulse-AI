from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class NemotronTrendItem(BaseModel):
    rank: int
    trend_name: str
    trend_score: float
    confidence: float
    momentum_score: float
    mention_count: int
    platform_breakdown: Dict[str, int]
    growth_rate: Optional[float] = None
    category: Optional[str] = None
    supporting_keywords: List[str] = Field(default_factory=list)
    is_demo: bool = False


class NemotronPayload(BaseModel):
    generated_at: str
    time_window: str = "7d"
    source_platforms: List[str]
    total_observations_analyzed: int
    data_mode: str = "demo"  # live_youtube, full_live, partial_live, demo
    live_observations_count: int = 0
    demo_observations_count: int = 0
    trends: List[NemotronTrendItem]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NemotronHandoffResponse(BaseModel):
    handoff_id: str
    status: str  # sent, failed, simulated, previewed
    endpoint_used: Optional[str] = None
    status_code: Optional[int] = None
    response_summary: Optional[str] = None
    error_detail: Optional[str] = None
    timestamp: datetime
