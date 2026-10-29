import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class CollectedContent(Base):
    __tablename__ = "collected_content"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = Column(String(32), nullable=False, index=True)  # reddit, instagram, youtube
    external_id = Column(String(255), nullable=False)
    title = Column(String(512), nullable=True)
    content_text = Column(Text, nullable=False)
    author_id = Column(String(128), nullable=True)
    permalink = Column(String(1024), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    collected_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    raw_metrics = Column(JSON, default=dict)  # upvotes, views, comments, likes
    normalized_engagement = Column(Float, default=0.0)
    is_fashion_related = Column(Boolean, default=True, index=True)
    fashion_confidence = Column(Float, default=1.0)
    extracted_terms = Column(JSON, default=list)
    is_demo = Column(Boolean, default=False, index=True)
    
    __table_args__ = (
        UniqueConstraint("platform", "external_id", name="uq_platform_external_id"),
        Index("ix_content_platform_pubdate", "platform", "published_at"),
    )


class Trend(Base):
    __tablename__ = "trends"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False, unique=True, index=True)
    category = Column(String(64), nullable=False, default="General Streetwear", index=True)
    description = Column(Text, nullable=True)
    current_rank = Column(Integer, nullable=True, index=True)
    current_score = Column(Float, default=0.0, index=True)
    confidence = Column(Float, default=0.0)
    momentum_score = Column(Float, default=0.0)
    growth_rate = Column(Float, nullable=True)  # Percentage or None if zero-baseline
    growth_status = Column(String(32), default="emerging")  # rising, steady, peaking, emerging, insufficient_data
    mention_count = Column(Integer, default=0)
    total_engagement = Column(Float, default=0.0)
    platform_breakdown = Column(JSON, default=dict)  # {"reddit": 10, "instagram": 20, "youtube": 5}
    first_seen = Column(DateTime(timezone=True), default=utcnow)
    last_seen = Column(DateTime(timezone=True), default=utcnow)
    time_window = Column(String(16), default="7d")
    supporting_keywords = Column(JSON, default=list)
    representative_references = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    
    observations = relationship("TrendObservation", back_populates="trend", cascade="all, delete-orphan")


class TrendObservation(Base):
    __tablename__ = "trend_observations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trend_id = Column(String(36), ForeignKey("trends.id", ondelete="CASCADE"), nullable=False, index=True)
    observation_window_start = Column(DateTime(timezone=True), nullable=False)
    observation_window_end = Column(DateTime(timezone=True), nullable=False)
    mention_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    trend_score = Column(Float, default=0.0)
    platform = Column(String(32), default="aggregated")  # reddit, instagram, youtube, aggregated
    recorded_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    
    trend = relationship("Trend", back_populates="observations")


class CollectionJob(Base):
    __tablename__ = "collection_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = Column(String(32), nullable=False)  # all, reddit, instagram, youtube
    status = Column(String(32), nullable=False, default="pending")  # pending, running, completed, failed, partial
    records_collected = Column(Integer, default=0)
    records_new = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), default=utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    trigger_type = Column(String(32), default="manual")  # manual, scheduled
    is_demo = Column(Boolean, default=False)


class ConnectorStatus(Base):
    __tablename__ = "connector_statuses"
    
    platform = Column(String(32), primary_key=True)  # reddit, instagram, youtube
    is_configured = Column(Boolean, default=False)
    is_authorized = Column(Boolean, default=False)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    last_error_message = Column(Text, nullable=True)
    total_records_ingested = Column(Integer, default=0)
    rate_limit_info = Column(JSON, default=dict)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class NemotronHandoff(Base):
    __tablename__ = "nemotron_handoffs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    payload = Column(JSON, nullable=False)
    status = Column(String(32), nullable=False)  # previewed, sent, failed, simulated
    response_status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, index=True)
