import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.core.logging import logger
from app.database.session import AsyncSessionLocal
from app.services.collection_service import collection_service
from app.services.trend_service import trend_service

scheduler = AsyncIOScheduler()


async def scheduled_collection_job():
    """Runs periodic ingestion and trend recalculation in background."""
    logger.info("Executing scheduled social media fashion trend collection job...")
    async with AsyncSessionLocal() as db:
        try:
            job = await collection_service.run_collection(
                db=db,
                platform_filter="all",
                trigger_type="scheduled",
                allow_demo_fallback=settings.ENABLE_DEMO_DATA_FALLBACK
            )
            logger.info(f"Scheduled collection finished. New records: {job.records_new}")
            
            # Recalculate trends
            await trend_service.detect_and_update_trends(db=db)
            logger.info("Scheduled trend recalculation complete.")
        except Exception as ex:
            logger.error(f"Error during scheduled collection: {str(ex)}")


def start_scheduler():
    """Starts the background worker scheduler if interval > 0."""
    if settings.COLLECTION_INTERVAL_MINUTES > 0:
        scheduler.add_job(
            scheduled_collection_job,
            "interval",
            minutes=settings.COLLECTION_INTERVAL_MINUTES,
            id="social_trend_collector",
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"Scheduler started: running every {settings.COLLECTION_INTERVAL_MINUTES} minutes.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
