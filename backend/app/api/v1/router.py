from fastapi import APIRouter
from app.api.v1.endpoints import health, connectors, collection, trends, analytics, nemotron

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(connectors.router)
api_router.include_router(collection.router)
api_router.include_router(trends.router)
api_router.include_router(analytics.router)
api_router.include_router(nemotron.router)
