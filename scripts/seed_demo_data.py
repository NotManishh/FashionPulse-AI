import asyncio
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.init_db import init_db, seed_initial_connector_statuses
from app.database.session import AsyncSessionLocal
from app.services.collection_service import collection_service
from app.services.trend_service import trend_service
from app.core.logging import logger


async def main():
    logger.info("Initializing database and seeding fashion observations...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        await seed_initial_connector_statuses(session)
        logger.info("Connector statuses initialized.")
        
        # Trigger collection with demo fallback
        job = await collection_service.run_collection(
            db=session,
            platform_filter="all",
            trigger_type="manual",
            allow_demo_fallback=True
        )
        logger.info(f"Ingestion complete: {job.records_new} new posts ingested.")
        
        # Calculate trends
        trends = await trend_service.detect_and_update_trends(db=session, days_window=7)
        logger.info(f"Trend intelligence calculated: {len(trends)} top trends ranked.")
        for t in trends:
            logger.info(f"  #{t.current_rank} {t.name} (Score: {t.current_score}, Status: {t.growth_status})")

    logger.info("Database seeding complete. Application is ready to launch!")


if __name__ == "__main__":
    asyncio.run(main())
