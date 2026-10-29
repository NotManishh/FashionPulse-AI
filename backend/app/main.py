from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.database.init_db import init_db, seed_initial_connector_statuses
from app.database.session import AsyncSessionLocal
from app.api.v1.router import api_router
from app.workers.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_initial_connector_statuses(session)
    
    # Start scheduler if not in testing
    if settings.ENVIRONMENT != "testing":
        start_scheduler()
        
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    stop_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Live Social Media Fashion Trend Detection and Intelligence Platform with NVIDIA Nemotron handoff interface.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Top-level health check endpoint for standard container probes
@app.get("/health", tags=["System"])
async def root_health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
