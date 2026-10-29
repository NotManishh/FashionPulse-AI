from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import async_engine, Base
from app.models.entities import ConnectorStatus, Trend
from app.core.logging import logger


async def init_db():
    """Initializes tables and default connector state."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        def ensure_trend_is_demo_column(connection):
            res = connection.exec_driver_sql("PRAGMA table_info(trends)").fetchall()
            cols = [r[1] for r in res]
            if "is_demo" not in cols and len(cols) > 0:
                connection.exec_driver_sql("ALTER TABLE trends ADD COLUMN is_demo BOOLEAN DEFAULT 0")

        await conn.run_sync(ensure_trend_is_demo_column)
    logger.info("Database tables initialized successfully.")


async def seed_initial_connector_statuses(session: AsyncSession):
    """Ensure all 3 platform connector status rows exist."""
    platforms = ["reddit", "instagram", "youtube"]
    for plat in platforms:
        result = await session.execute(
            select(ConnectorStatus).where(ConnectorStatus.platform == plat)
        )
        existing = result.scalar_one_or_none()
        if not existing:
            status = ConnectorStatus(
                platform=plat,
                is_configured=False,
                is_authorized=False,
                total_records_ingested=0,
                rate_limit_info={"remaining": "N/A", "reset": None}
            )
            session.add(status)
    await session.commit()
