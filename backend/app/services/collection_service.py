import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.connectors.base import BaseSocialConnector, NormalizedContentItem
from app.connectors.reddit import reddit_connector
from app.connectors.instagram import instagram_connector
from app.connectors.youtube import youtube_connector
from app.models.entities import CollectedContent, CollectionJob, ConnectorStatus
from app.ml.fashion_classifier import fashion_classifier
from app.ml.trend_extractor import trend_extractor
from app.ml.scoring import scoring_engine
from app.core.logging import logger


class CollectionService:
    """Manages ingestion of social media fashion content across all platforms."""

    def __init__(self):
        self.connectors: Dict[str, BaseSocialConnector] = {
            "reddit": reddit_connector,
            "instagram": instagram_connector,
            "youtube": youtube_connector
        }

    async def run_collection(
        self,
        db: AsyncSession,
        platform_filter: str = "all",
        trigger_type: str = "manual",
        allow_demo_fallback: bool = True
    ) -> CollectionJob:
        """
        Executes ingestion for specified or all connectors, performs deduplication,
        runs ML classification, and persists results.
        """
        job = CollectionJob(
            id=str(uuid.uuid4()),
            platform=platform_filter,
            status="running",
            records_collected=0,
            records_new=0,
            started_at=datetime.now(timezone.utc),
            trigger_type=trigger_type,
            is_demo=False
        )
        db.add(job)
        await db.commit()

        target_platforms = (
            list(self.connectors.keys())
            if platform_filter == "all"
            else [platform_filter]
        )

        # Check if any live configured connectors exist
        configured_platforms = {
            plat: conn for plat, conn in self.connectors.items() if conn.validate_credentials()
        }

        total_collected = 0
        total_new = 0
        has_errors = False
        error_messages = []
        is_any_demo = False

        for plat in target_platforms:
            connector = self.connectors.get(plat)
            if not connector:
                continue

            # If live connectors exist, unconfigured platforms MUST NOT fabricate mock data
            is_plat_configured = connector.validate_credentials()
            if configured_platforms and not is_plat_configured:
                if plat == "reddit":
                    msg = "Reddit for Researchers (RFR) ingestion skipped (disabled pending BigQuery Analytics Hub access)."
                elif plat == "instagram":
                    msg = "Instagram Graph API v26.0 ingestion skipped (credentials not configured)."
                else:
                    msg = f"{plat} connector skipped (unconfigured)."
                logger.info(msg)
                connector.record_error(msg)
                await self._update_connector_status(db, plat, connector)
                continue

            # If NO connectors are configured at all and fallback is disabled, abort cleanly
            if not configured_platforms and not allow_demo_fallback:
                msg = f"{plat} credentials not configured and demo fallback is disabled."
                connector.record_error(msg)
                await self._update_connector_status(db, plat, connector)
                continue

            try:
                raw_items: List[NormalizedContentItem] = await connector.fetch_recent_content()
                total_collected += len(raw_items)

                for item in raw_items:
                    if item.is_demo:
                        is_any_demo = True

                    # Deduplication check
                    existing = await db.execute(
                        select(CollectedContent).where(
                            CollectedContent.platform == item.platform,
                            CollectedContent.external_id == item.external_id
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    # ML Fashion Classification
                    is_fashion, confidence = fashion_classifier.classify(item.content_text)

                    # Extract candidate entities & keywords
                    extracted_candidates = trend_extractor.extract_candidate_terms(item.content_text)
                    extracted_names = [c["normalized_name"] for c in extracted_candidates]

                    # Engagement normalization
                    normalized_eng = scoring_engine.normalize_engagement(
                        item.platform, item.raw_metrics
                    )

                    new_record = CollectedContent(
                        id=str(uuid.uuid4()),
                        platform=item.platform,
                        external_id=item.external_id,
                        title=item.title,
                        content_text=item.content_text,
                        author_id=item.author_id,
                        permalink=item.permalink,
                        published_at=item.published_at,
                        collected_at=datetime.now(timezone.utc),
                        raw_metrics=item.raw_metrics,
                        normalized_engagement=normalized_eng,
                        is_fashion_related=is_fashion,
                        fashion_confidence=confidence,
                        extracted_terms=extracted_names,
                        is_demo=item.is_demo
                    )
                    db.add(new_record)
                    total_new += 1

                # Update connector database status
                await self._update_connector_status(db, plat, connector)

            except Exception as ex:
                has_errors = True
                msg = f"{plat} connector error: {str(ex)}"
                error_messages.append(msg)
                logger.error(msg)
                connector.record_error(str(ex))
                await self._update_connector_status(db, plat, connector)

        job.status = "completed" if not has_errors else ("partial" if total_new > 0 else "failed")
        job.records_collected = total_collected
        job.records_new = total_new
        job.completed_at = datetime.now(timezone.utc)
        # Job is marked demo ONLY IF no live records exist and all collected records are demo
        job.is_demo = bool(not configured_platforms and is_any_demo)
        if error_messages:
            job.error_message = "; ".join(error_messages)

        await db.commit()
        await db.refresh(job)
        return job

    async def _update_connector_status(self, db: AsyncSession, platform: str, connector: BaseSocialConnector):
        """Updates or creates runtime status in DB."""
        info = connector.get_status()
        existing = await db.execute(
            select(ConnectorStatus).where(ConnectorStatus.platform == platform)
        )
        row = existing.scalar_one_or_none()
        if not row:
            row = ConnectorStatus(platform=platform)
            db.add(row)

        row.is_configured = info.is_configured
        row.is_authorized = info.is_authorized
        row.last_success_at = info.last_success_at
        row.last_error_at = info.last_error_at
        row.last_error_message = info.last_error_message
        row.total_records_ingested += info.total_records_ingested
        row.rate_limit_info = info.rate_limit_info
        row.updated_at = datetime.now(timezone.utc)
        await db.commit()


collection_service = CollectionService()
