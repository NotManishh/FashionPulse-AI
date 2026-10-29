# Architecture Specification — FashionPulse AI

## System Overview

FashionPulse AI is an automated multi-platform social media intelligence and trend forecasting system built using a decoupled microservice architecture:

```
[ Reddit API ]    [ Instagram Graph API ]    [ YouTube Data API ]
       │                     │                        │
       └─────────────┬───────┴────────────────────────┘
                     ▼
           [ Platform Connectors ]
       (Normalization & Deduplication)
                     │
                     ▼
          [ ML Intelligence Pipeline ]
    ├── Fashion Domain Classifier (signal vs noise)
    ├── Entity & Syntactic Phrase Extractor
    ├── Synonym Taxonomy Normalization
    ├── TF-IDF & Cosine Similarity Clusterer
    └── Multi-Factor Composite Trend Scoring Engine
                     │
                     ▼
      [ PostgreSQL / SQLite Persistence ]
    (CollectedContent, Trends, TrendObservations)
                     │
                     ├───▶ [ FastAPI REST Services ]
                     │             │
                     │             ▼
                     │     [ React 18 / Vite Dashboard ]
                     ▼
       [ Downstream NVIDIA Nemotron Adapter ]
           (Structured Intelligence Payload)
```

---

## 1. Mathematical Scoring Formula

The platform distinguishes **popularity** (overall volume), **momentum** (velocity of acceleration), and **emerging trends** (rising activity with sufficient baseline evidence).

Composite Trend Score $S_{\text{trend}} \in [0, 100]$:

$$S_{\text{trend}} = \left( w_f \cdot S_{\text{freq}} + w_m \cdot S_{\text{mom}} + w_e \cdot S_{\text{eng}} + w_c \cdot S_{\text{cross}} + w_r \cdot S_{\text{rec}} \right) \times (0.6 + 0.4 \cdot C)$$

Where:
- $w_f = 0.30$ (Mention frequency weight)
- $w_m = 0.25$ (Momentum velocity weight)
- $w_e = 0.20$ (Normalized engagement weight)
- $w_c = 0.15$ (Cross-platform presence weight)
- $w_r = 0.10$ (Recency exponential decay weight)
- $C \in [0.1, 1.0]$: Confidence factor derived from observation count, platform diversity, and classifier certainty.

### Logarithmic Engagement Scaling
Raw engagement counts are scaled logarithmically to prevent viral outliers from distorting rankings:

$$\text{Engagement}_{\text{YouTube}} = 1.5 \ln(1 + \text{views}) + 3.0 \ln(1 + \text{likes}) + 4.0 \ln(1 + \text{comments})$$
$$\text{Engagement}_{\text{Reddit}} = 3.5 \ln(1 + \max(0, \text{score})) + 4.5 \ln(1 + \text{comments})$$
$$\text{Engagement}_{\text{Instagram}} = 3.0 \ln(1 + \text{likes}) + 5.0 \ln(1 + \text{comments})$$

### Zero-Baseline Handling
When a trend has 0 mentions in the previous baseline window:
- Growth percentage is reported as `None` rather than inventing an artificial 1000% spike.
- Growth status is marked as `emerging`.
- If current mentions $< 3$, status is marked as `insufficient_data`.

---

## 2. Database Schema Design

- **`collected_content`**: Ingested social posts with unique constraint `(platform, external_id)` to enforce deduplication.
- **`trends`**: Top discovered trends with dynamic ranking, categories, velocity, and keywords.
- **`trend_observations`**: Time-series snapshot log tracking historical velocity over time.
- **`connector_statuses`**: Health, authorization, error telemetry, and rate limit counters for each connector.
- **`collection_jobs`**: Audit trail of every scheduled and manual ingestion run.
- **`nemotron_handoffs`**: Audit log of all model handoff payloads, status codes, and model responses.
