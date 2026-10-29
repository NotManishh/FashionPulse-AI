from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

# Explicitly resolve root .env path to ensure it loads regardless of process CWD
_ROOT_DIR = Path(__file__).resolve().parents[3]
_ROOT_ENV_FILE = _ROOT_DIR / ".env"


_DB_PATH = (_ROOT_DIR / "fashionpulse.db").as_posix()


class Settings(BaseSettings):
    PROJECT_NAME: str = "FashionPulse AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="development | testing | production")
    
    # Database
    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{_DB_PATH}",
        description="Async SQLAlchemy database URL. Defaults to SQLite for local development, postgresql+asyncpg for production."
    )
    SYNC_DATABASE_URL: Optional[str] = Field(
        default=f"sqlite:///{_DB_PATH}",
        description="Sync database URL for Alembic migrations."
    )

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def normalize_db_url(cls, v: str) -> str:
        if v.startswith("sqlite+aiosqlite:///./"):
            rel_file = v.replace("sqlite+aiosqlite:///./", "")
            return f"sqlite+aiosqlite:///{(_ROOT_DIR / rel_file).as_posix()}"
        return v

    @field_validator("SYNC_DATABASE_URL", mode="after")
    @classmethod
    def normalize_sync_db_url(cls, v: Optional[str]) -> Optional[str]:
        if v and v.startswith("sqlite:///./"):
            rel_file = v.replace("sqlite:///./", "")
            return f"sqlite:///{(_ROOT_DIR / rel_file).as_posix()}"
        return v
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]
    
    # Reddit for Researchers (RFR) Config — Google BigQuery Analytics Hub (BQAH)
    ENABLE_REDDIT_RFR_INGESTION: bool = Field(
        default=False,
        description="Disabled by default until academic authorization via the Reddit for Researchers (RFR) BigQuery program is granted."
    )
    # Alias for backward compatibility
    ENABLE_LIVE_REDDIT_COLLECTOR: bool = False
    
    # BigQuery Analytics Hub configuration (provisioned upon RFR application approval)
    RFR_GCP_PROJECT_ID: Optional[str] = Field(
        default=None,
        description="Google Cloud Project ID provisioned/linked for BigQuery Analytics Hub research access."
    )
    RFR_DATASET_NAME: Optional[str] = Field(
        default=None,
        description="Subscriber dataset name linked in BigQuery from the Reddit for Researchers Analytics Hub shared listing."
    )
    RFR_TABLE_NAME: str = Field(
        default="posts",
        description="Standard RFR BigQuery table name for post submissions."
    )
    RFR_CREDENTIALS_PATH: Optional[str] = Field(
        default=None,
        description="Path to service account JSON key file, or None if using Google Application Default Credentials."
    )
    REDDIT_SUBREDDITS: List[str] = [
        "streetwear",
        "malefashionadvice",
        "femalefashionadvice",
        "fashion",
        "OUTFITS",
        "Sneakers"
    ]
    
    # Instagram Connector Config (Meta Graph API v26.0+)
    INSTAGRAM_API_VERSION: str = "v26.0"
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_BUSINESS_ACCOUNT_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    INSTAGRAM_HASHTAGS: List[str] = [
        "fashiontrends",
        "streetwearfashion",
        "ootd",
        "coquetteaesthetic",
        "quietluxury",
        "vintageclothing",
        "techwear"
    ]
    
    # YouTube Connector Config (YouTube Data API v3)
    YOUTUBE_API_KEY: Optional[str] = None
    YOUTUBE_SEARCH_TERMS: List[str] = [
        "streetwear haul outfit trends 2026",
        "oversized hoodie aesthetic streetwear",
        "wide leg baggy denim jeans style",
        "cargo pants utility trousers fashion",
        "sneakers footwear trend aesthetic 2026",
        "chunky loafers boots styling fashion",
        "quiet luxury old money aesthetic outfit",
        "tailored blazer minimalist fashion style",
        "knitwear sweater winter fashion haul",
        "statement outerwear jacket trench coats",
        "fashion accessories jewelry styling haul",
        "maxi dress skirt seasonal silhouette trends",
        "emerging clothing trends 2026 predictions"
    ]
    
    # NVIDIA Nemotron Adapter Settings
    NEMOTRON_ENDPOINT_URL: Optional[str] = None
    NEMOTRON_API_KEY: Optional[str] = None
    NEMOTRON_MODEL_NAME: str = "nvidia/nemotron-4-340b-instruct"
    NEMOTRON_TIMEOUT_SECONDS: float = 30.0
    
    # Platform Collection & Demo Settings
    COLLECTION_INTERVAL_MINUTES: int = 60
    ENABLE_DEMO_DATA_FALLBACK: bool = True
    MAX_ITEMS_PER_FETCH: int = 50
    DATA_RETENTION_DAYS: int = 90
    
    # Scoring Engine Weights (Configurable)
    WEIGHT_FREQUENCY: float = 0.30
    WEIGHT_MOMENTUM: float = 0.25
    WEIGHT_ENGAGEMENT: float = 0.20
    WEIGHT_CROSS_PLATFORM: float = 0.15
    WEIGHT_RECENCY: float = 0.10
    
    # Minimum sample threshold to declare confident trend
    MIN_OBSERVATION_THRESHOLD: int = 3
    
    model_config = {
        "env_file": [str(_ROOT_ENV_FILE), ".env"],
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings()
