from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone
from app.database.session import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health status and database connectivity check."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as ex:
        db_status = f"unhealthy: {str(ex)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
