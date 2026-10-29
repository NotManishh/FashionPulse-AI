# Social Media API Credentials & Setup Guide

This guide details the exact requirements, platform policies, and setup procedures to transition FashionPulse AI from local demonstration mode to genuine, authenticated social media collection across Reddit, Instagram, and YouTube.

---

## 1. Reddit (Reddit for Researchers Program via BigQuery Analytics Hub)

### Academic Research Access Architecture: Google BigQuery Analytics Hub (BQAH)
Official academic research access to Reddit is provided exclusively through the **Reddit for Researchers (RFR)** program. Reddit partners with Google Cloud to distribute research datasets via **Google BigQuery Analytics Hub (BQAH)**.

> [!CAUTION]
> **RFR Does NOT Grant Ordinary Reddit OAuth Data API Access**  
> Approval for Reddit for Researchers does **not** provide Reddit OAuth Data API client credentials (`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, or `oauth.reddit.com`). Ordinary developer keys created at `reddit.com/prefs/apps` are strictly for developer applications, moderation bots, and internal scripts. Attempting to scrape or harvest research datasets through standard OAuth endpoints violates Reddit's Responsible Builder Policy and Developer Terms.

### Data Availability & Update Cadence: Not Real-Time
- **5-Year Rolling Lookback:** The RFR research repository maintains a 5-year rolling archive of Reddit platform activity across public subreddits.
- **6-Month Historical Lag:** Datasets are subject to a **6-month historical blackout lag** before release to researchers to safeguard user privacy and allow moderation actions to settle.
- **Monthly Batch Refresh:** Reddit pushes updates to the BigQuery Analytics Hub listing on a **monthly batch cycle**.
- **Not Real-Time:** **The Reddit connector is NOT a real-time stream.** It is a historical and longitudinal academic batch pipeline. In contrast, live real-time signals in FashionPulse AI are collected via the Instagram (Meta Graph API v26.0) and YouTube Data API v3 connectors.

### Approved Dataset Schema
The RFR BigQuery Analytics Hub dataset exposes standardized tables for approved research:
1. **`posts` Table Schema:**
   - `id` (STRING): Unique submission identifier.
   - `name` (STRING): Reddit fullname prefix (e.g., `t3_xyz123`).
   - `title` (STRING): Submission title.
   - `selftext` (STRING): Text content of post (or empty string for link/media posts).
   - `url` (STRING): Link destination or external media URL.
   - `author` (STRING): Masked / pseudonymized author identifier.
   - `subreddit` (STRING): Subreddit display name (e.g., `streetwear`, `malefashionadvice`).
   - `score` (INTEGER): Net upvote score.
   - `upvote_ratio` (FLOAT): Upvote-to-downvote ratio.
   - `num_comments` (INTEGER): Comment count.
   - `created_utc` (TIMESTAMP / STRING): Submission creation timestamp.
   - `permalink` (STRING): Canonical Reddit permalink path.
2. **`comments` Table Schema:**
   - `id`, `name`, `link_id`, `parent_id`, `body`, `author`, `subreddit`, `score`, `created_utc`, `permalink`.

### Required Onboarding Information & Missing Credentials
Access to the BQAH listing is provisioned directly to an approved researcher's `@redditresearchers.com` institutional identity. Because access is established inside Google Cloud Platform, the following environment variables cannot be generated automatically and must be filled in once onboarding is finalized:

| Variable | Description | Status Before Approval |
| :--- | :--- | :--- |
| `ENABLE_REDDIT_RFR_INGESTION` | Master boolean switch enabling BigQuery ingestion | `false` (Disabled by default) |
| `RFR_GCP_PROJECT_ID` | Your GCP Project ID where the BQAH listing is linked | Missing (Provided by researcher's GCP account) |
| `RFR_DATASET_NAME` | The linked dataset name in your GCP BigQuery instance | Missing (Created upon subscribing to BQAH listing) |
| `RFR_TABLE_NAME` | The target table to query | Defaults to `posts` |
| `RFR_CREDENTIALS_PATH` | Path to GCP Service Account JSON key (or use ADC) | Missing (Created in GCP Console IAM) |

### RFR Research Compliance & Ethical Constraints
1. **AI / LLM Model Training Prohibition:** Reddit data obtained through RFR **must NOT be used to train artificial intelligence or large language models** without explicit, separate written authorization from Reddit. FashionPulse AI strictly processes content for statistical trend velocity, sentiment scoring, and cross-platform popularity indexing.
2. **Author Privacy & Anonymization:** Author handles are preserved as masked/hashed strings; researchers must not attempt re-identification or deanonymization.
3. **Right to be Forgotten (48-Hour Compliance):** User deletion and moderation purges synced in monthly BQAH batch releases must be respected; local raw post archives must sync with current dataset state.

### How to Re-Enable the Reddit Connector After RFR Approval
Once your research proposal is formally approved and your GCP project subscribes to the RFR listing in BigQuery Analytics Hub:
1. Ensure `google-cloud-bigquery` is installed in your Python environment (`pip install google-cloud-bigquery`).
2. Generate a Service Account key with `BigQuery Data Viewer` and `BigQuery Job User` roles in your GCP project.
3. Update your `.env` configuration:
   ```bash
   ENABLE_REDDIT_RFR_INGESTION=true
   RFR_GCP_PROJECT_ID=your-gcp-research-project-id
   RFR_DATASET_NAME=reddit_researchers_dataset
   RFR_TABLE_NAME=posts
   RFR_CREDENTIALS_PATH=/path/to/service_account_key.json
   ```
4. Restart the backend service. FashionPulse AI will query BigQuery directly and ingest approved research records.
5. While disabled or before credentials are configured, FashionPulse AI operates in demonstration mode (`is_demo=True`), ensuring pipeline stability.

---

## 2. Meta Graph API (Instagram v26.0)

### Version Verification & Lifecycle
Meta Graph API **v19.0 expired on May 21, 2026**, **v20.0 expired on September 24, 2026**, and **v21.0 expires on January 21, 2027**. FashionPulse AI uses **Meta Graph API v26.0** (released July 29, 2026), the latest supported production release.

> [!IMPORTANT]
> **Upgrading the API Version Does NOT Grant Restricted Feature Access**  
> Specifying `v26.0` ensures endpoint compatibility and longevity, but does **not** bypass Meta's App Review requirements. Access to public hashtag discovery edges strictly requires approval for the **Instagram Public Content Access (IPCA)** feature.

### Prerequisites, Permissions & Restricted Feature Access
1. **Instagram Account Type:** Must be an **Instagram Professional Account** (Business or Creator), linked to a verified Facebook Page.
2. **Permissions Required:**
   - `instagram_basic`: Allows reading basic Instagram account details.
   - `pages_read_engagement` (or `business_management`): Authorizes the app to act on behalf of the connected Facebook Page.
3. **Restricted Feature — Instagram Public Content Access (IPCA):**
   - Querying hashtag search and recent media endpoints (`/ig_hashtag_search` and `/{hashtag_id}/recent_media`) strictly requires the **Instagram Public Content Access** feature.
   - **Production:** Requires Meta App Review, Business Verification, and contractual acceptance of Meta's Developer Terms.
   - **Development Mode:** In Development Mode, IPCA endpoints can only be queried by users who have been explicitly added as Administrators, Developers, or Testers of the Meta Developer App.

### Exact Endpoints & Field Specifications (v26.0)
- **Hashtag Lookup:**  
  `GET https://graph.facebook.com/v26.0/ig_hashtag_search?user_id={INSTAGRAM_BUSINESS_ACCOUNT_ID}&q={hashtag}&access_token={ACCESS_TOKEN}`
- **Recent Media Fetch:**  
  `GET https://graph.facebook.com/v26.0/{hashtag_id}/recent_media?user_id={INSTAGRAM_BUSINESS_ACCOUNT_ID}&fields=id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count&limit=20&access_token={ACCESS_TOKEN}`
- **Field & Query Limitations:**
  - **No `username` field:** Meta strictly prohibits requesting the `username` field on hashtag media; doing so returns an HTTP 400 error.
  - **No Emojis:** Hashtag search terms (`q`) cannot contain emojis or punctuation.
  - **24-Hour Recency:** The `recent_media` edge only returns public media published within the last 24 hours.
  - **Hashtag Rolling Limit:** An Instagram Business account can query a maximum of **30 unique hashtags** within any rolling 7-day period (both hashtag searches and media requests count against this quota).

### Setup Instructions
1. Create an App of type **"Business"** at [developers.facebook.com/apps](https://developers.facebook.com/apps/).
2. Add the **Instagram Graph API** product.
3. Under **App Review > Permissions and Features**, ensure `instagram_basic`, `pages_read_engagement`, and **Instagram Public Content Access** are requested and approved.
4. Obtain a User Access Token with the required scopes using the Graph API Explorer.
5. Exchange for a 60-day long-lived token:
   ```bash
   GET https://graph.facebook.com/v26.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={SHORT_LIVED_TOKEN}
   ```
6. Retrieve your Business Account ID:
   ```bash
   GET https://graph.facebook.com/v26.0/me/accounts?access_token={LONG_LIVED_TOKEN}
   GET https://graph.facebook.com/v26.0/{PAGE_ID}?fields=instagram_business_account&access_token={LONG_LIVED_TOKEN}
   ```
7. Configure `.env`:
   ```bash
   INSTAGRAM_API_VERSION=v26.0
   INSTAGRAM_ACCESS_TOKEN=your_long_lived_token_here
   INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id_here
   INSTAGRAM_APP_SECRET=your_app_secret_here
   ```

---

## 3. YouTube Data API v3 (Quota Architecture & Batch Hydration)

### Overview & Quota Allocation (Google Cloud)
The YouTube Data API v3 employs a dual-bucket quota architecture:
1. **Dedicated Search Quota Bucket:**
   - Google allocates a dedicated default limit of **100 `search.list` calls per day** per project.
   - Each search query consumes **1 call** from this search bucket.
2. **General Quota Pool:**
   - Standard read endpoints draw from a separate **10,000 units per day** combined pool.
   - A `videos.list` call costs **1 unit** from this general pool and can batch up to **50 video IDs** per request.
3. **Daily Reset:** Quotas reset daily at midnight Pacific Time (PT).

### FashionPulse AI Quota Optimization
- **Two-Phase Hydration:** FashionPulse AI executes minimal search queries across high-priority fashion keywords (consuming only 2 calls from the 100-call search bucket per ingestion run), then batches up to 50 discovered IDs into a single `videos.list` call (costing just 1 general unit).
- **Search Bucket Preservation:** The connector's `verify_authorization()` method deliberately queries `videos.list?chart=mostPopular&maxResults=1` (1 general unit), completely avoiding `search.list` during health checks.
- **Quota Extension:** To scale beyond 100 search queries per day, submit the **YouTube API Services - Audit and Quota Extension Form** in the Google Cloud Console.

### Setup Instructions
1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select your project and enable the **YouTube Data API v3**.
3. Under **APIs & Services > Credentials**, create an **API key**.
4. Restrict the key to only authorize the **YouTube Data API v3**.
5. Configure `.env`:
   ```bash
   YOUTUBE_API_KEY=AIzaSy...
   ```

---

## 4. Summary of Required User Actions

| Platform | Required User Action Before Live Ingestion | Approval Type |
| :--- | :--- | :--- |
| **Reddit** | Submit application through **Reddit for Researchers (RFR)**. Upon BQAH listing grant to your `@redditresearchers.com` identity, link dataset to your GCP project and set `ENABLE_REDDIT_RFR_INGESTION=true` with service account credentials. Monthly batch cadence (not real-time). | Formal RFR Program Approval & GCP BQAH Grant |
| **Instagram** | Link IG Business/Creator account to Facebook Page; obtain Meta App Access Token with `instagram_basic` and approved **Instagram Public Content Access** (IPCA) feature on Graph API v26.0. | Meta App Review (or Dev Mode) |
| **YouTube** | Generate API Key on Google Cloud Console restricted to YouTube Data API v3. Optional quota extension if > 100 search calls/day needed. | Self-Service Instant API Key |
| **Nemotron** | Set `NEMOTRON_ENDPOINT_URL` and `NEMOTRON_API_KEY` in `.env` if connecting downstream NVIDIA NIM/OpenAI inference. | Optional Handoff |
