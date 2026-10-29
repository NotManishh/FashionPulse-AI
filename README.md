# FashionPulse AI — Live Social Media Fashion Trend Detection and Intelligence Platform

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-42%20Passed-emerald.svg)]()
[![Production Engine](https://img.shields.io/badge/Production%20Engine-YouTube%20v3%20Live-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

> **FashionPulse AI** is a real-time fashion intelligence platform that discovers, clusters, scores, and ranks emerging fashion trends dynamically from live social video streams using the **Google Cloud YouTube Data API v3**. The platform normalizes fashion entities, eliminates non-fashion noise using ML classification, prevents duplicates via external ID deduplication, and formats structured downstream payloads for **NVIDIA Nemotron** reasoning models.

---

## Architecture Overview (YouTube-Only Production Engine)

```
[ YouTube Data API v3 ]
        │ (Real-time search.list & videos.list batching)
        ▼
[ Ingestion & Deduplication Service ]
        │ Checks (platform, external_id) ➔ Skips duplicate videos
        │ Reports: records_collected vs. records_new
        ▼
[ ML Fashion Classifier (Confidence >= 0.35) ]
        ├── True  ➔ 206 Validated Fashion Observations
        └── False ➔ 38 Non-Fashion Noise Videos (Excluded from scoring)
        ▼
[ Entity Extractor & Semantic Clustering ]
        │ Normalizes synonyms (e.g. "baggy denim" ➔ "Wide-Leg & Baggy Denim")
        │ Preserves distinct fashion silhouettes, footwear, and tailoring
        ▼
[ Mathematical Trend Scoring & Tie-Breaker Engine ]
        │ Factors: mention frequency, momentum, log(engagement), recency decay
        │ Monotonically descending score sorting + sequential rank assignment (1 to N)
        │ Computes distinct Top 10 Fashion Trends based on genuine live evidence
        ▼
[ Haute-Couture UI Dashboard ] ───► [ NVIDIA Nemotron Downstream Payload ]
(Live YouTube badges & metrics)      (Pure YouTube evidence, optional inference)
```

---

## Key Features

- **YouTube Data API v3 Sole Active Production Connector**:
  - Operates on a dedicated 100 search queries/day bucket + 10,000 units/day general quota pool with midnight PT reset.
  - Automatically deduplicates incoming videos by `external_id` so repeated ingestion never creates duplicate records.
  - Newly collected records (`records_collected`) versus newly inserted records (`records_new`) are reported and audited separately.
- **Noise Rejection & Count Reconciliation**:
  - Stores all fetched videos, but applies the **ML Fashion Classifier** before scoring.
  - Out of 244 stored live YouTube records, 206 are fashion-validated observations and 38 non-fashion vlogs are rejected as noise. The Nemotron preview and trend scoring analyze only validated fashion observations.
- **Strict Trend Ranking & Dynamic Length**:
  - Trends are globally sorted by score in descending order, with momentum and confidence as documented tie-breakers.
  - Sequential ranks (1 to 10) are assigned dynamically to genuine, distinct fashion trend clusters supported by live evidence.
- **Platform Attribution & Historical Record Preservation**:
  - Trend cards and analytics derive platform breakdowns exclusively from genuine supporting observations.
  - Historical database records from Reddit and Instagram are preserved in `fashionpulse.db` without deletion, but moved to an optional "Future Integrations" section and excluded from the live scoring pipeline.
  - Demo observations never enter live trend scoring when live observations are present.
- **Optional NVIDIA Nemotron Adapter**:
  - Generates structured top-trend JSON previews formatted with genuine YouTube evidence.
  - Remotely dispatched inference remains completely optional: if `NEMOTRON_ENDPOINT_URL` is omitted, the application reports a clear, non-blocking configuration notice rather than crashing or simulating fake completions.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Backend API** | Python 3.12 / 3.13, FastAPI, Pydantic V2, Uvicorn, SQLAlchemy 2.0, HTTPX, APScheduler |
| **Database** | SQLite with `aiosqlite` (Local Dev & Unit Tests), PostgreSQL compatible |
| **ML & NLP** | scikit-learn, TF-IDF vectorizers, Cosine Similarity clustering, custom fashion taxonomy |
| **Frontend** | React 18, TypeScript, Vite, Vanilla/Tailwind CSS, Lucide Icons, Recharts |
| **Active Ingestion** | Google Cloud YouTube Data API v3 |
| **Planned Extensions** | Reddit for Researchers (Google BigQuery Analytics Hub), Meta Instagram Graph API v26.0 |
| **AI Reasoning** | NVIDIA Nemotron adapter (optional downstream endpoint) |
| **Test Suite** | Pytest, Pytest-Asyncio (42 comprehensive test cases) |

---

## Windows PowerShell Startup Instructions

### 1. Configure the Environment
Ensure your Google Cloud YouTube API Key is configured in the root `.env` file:

```powershell
# In the project root (c:\Users\Manish\.gemini\antigravity-ide\scratch\fashionpulse-ai)
# Ensure .env contains:
YOUTUBE_API_KEY=AIzaSy...your_actual_key_here...
```

> **Note**: No other API keys are required to run the live application. Reddit and Instagram connectors are roadmapped future integrations and remain disabled without blocking live operation.

### 2. Start the Application via Dev Script
Run the automated Windows PowerShell runner from the project root:

```powershell
.\scripts\run_dev.ps1
```

This script:
1. Checks for the SQLite database (`fashionpulse.db`). If live data is already present, it **preserves** all existing live observations and skips demo seeding.
2. Starts the **FastAPI Backend** on `http://127.0.0.1:8000`.
3. Launches the **Vite Frontend Dev Server** on `http://localhost:5173`.

### 3. Or Start Services Manually in Separate PowerShell Terminals

**Terminal 1 — Backend API:**
```powershell
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend Application:**
```powershell
cd frontend
npm run dev
```

Open your browser to:
- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Interactive Backend API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Probe**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Testing & Verification

Run the full backend regression test suite (42 tests):

```powershell
python -m pytest backend/tests -v
```

Build the production frontend bundle:

```powershell
npm --prefix frontend run build
```

Verify live YouTube collection and deduplication:

```powershell
python -c "
import asyncio, sys
sys.path.insert(0, 'backend')
from app.database.session import AsyncSessionLocal
from app.services.collection_service import collection_service
async def test():
    async with AsyncSessionLocal() as db:
        job = await collection_service.run_collection(db, platform_filter='youtube', allow_demo_fallback=False)
        print(f'Ingested: collected={job.records_collected}, new={job.records_new}')
asyncio.run(test())
"
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health and database connectivity probe |
| `GET` | `/api/v1/connectors/status` | Live authorization and record telemetry (YouTube active, others roadmapped) |
| `POST` | `/api/v1/collection/run` | Triggers YouTube content ingestion, deduplicates, and updates trends |
| `GET` | `/api/v1/trends/top10` | Top fashion trends sorted strictly by trend score with tie-breakers |
| `GET` | `/api/v1/trends` | Filterable list of all active trends (search, category, status) |
| `GET` | `/api/v1/trends/{trend_id}` | Full detail view of a specific trend with YouTube evidence citations |
| `GET` | `/api/v1/trends/{trend_id}/history` | Historical velocity snapshots for time-series charts |
| `GET` | `/api/v1/analytics/overview` | Platform distribution, categories, velocity ratios (YouTube live stream) |
| `GET` | `/api/v1/analytics/platforms` | Per-platform post volume and engagement averages |
| `POST` | `/api/v1/nemotron/preview` | Generates downstream Nemotron payload preview using live YouTube evidence |
| `POST` | `/api/v1/nemotron/send` | Dispatches handoff to NVIDIA Nemotron endpoint (fails gracefully if unconfigured) |

---

## Security & Compliance

- **No Secrets in Frontend**: API keys reside solely in `.env` and are never serialized to the client.
- **Strict Deduplication**: All incoming video items are checked against `(platform, external_id)` prior to persistence.
- **Noise Isolation**: Content failing the fashion classification threshold is flagged `is_fashion_related=False` and excluded from downstream analysis.
- **No Mock Contamination**: When live YouTube data exists, demo fallback records are excluded from trend calculations.
