import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.connectors.base import BaseSocialConnector, NormalizedContentItem
from app.connectors.mock_data import get_demo_fashion_content
from app.core.config import settings
from app.core.logging import logger


class RedditRFRConnector(BaseSocialConnector):
    """
    Reddit for Researchers (RFR) Data Ingestion Adapter via Google BigQuery Analytics Hub (BQAH).

    Academic Access, Cadence & Compliance Architecture:
    1. Access Mechanism: Access to the official Reddit for Researchers program is provisioned
       exclusively through Google Cloud BigQuery Analytics Hub (BQAH). Accepted academic researchers
       receive an institutional @redditresearchers.com identity with multi-factor authentication (2FA)
       and subscribe to Reddit's shared dataset within their Google Cloud project.
       Ordinary Reddit OAuth Data API client credentials (client_id / client_secret) are NOT used
       for academic research access.
    2. Data Availability & Cadence (NOT Real-Time):
       - Lookback Window: 5-year rolling historical dataset.
       - Lag: Features a 6-month historical lag.
       - Update Cadence: Tables are updated on a monthly batch cadence (to synchronize user deletions,
         right-to-be-forgotten scrubbings, and community moderation actions).
       - This connector is strictly a batch historical research ingestion adapter, NOT a real-time streaming feed.
    3. Approved Dataset Schema (Posts Table):
       - id (STRING): Unique post identifier (e.g. '12abc34').
       - name (STRING): Fullname identifier (e.g. 't3_12abc34').
       - title (STRING): Submission title.
       - selftext (STRING): Post body markdown text.
       - url (STRING): Post URL / link target.
       - author (STRING): Anonymized / hashed user identifier per RFR privacy protocol.
       - subreddit (STRING): Subreddit community name (e.g. 'streetwear').
       - score (INTEGER): Net vote score.
       - upvote_ratio (FLOAT): Ratio of upvotes to total votes.
       - num_comments (INTEGER): Total comments registered on the post.
       - created_utc (TIMESTAMP): Post creation timestamp in UTC.
       - permalink (STRING): Relative URL path to the discussion thread.
    4. Missing Onboarding Details (Individually Assigned Upon Approval):
       - RFR_GCP_PROJECT_ID: The researcher's Google Cloud project ID provisioned for BigQuery Analytics Hub.
       - RFR_DATASET_NAME: The subscriber dataset name linked in BigQuery from the RFR shared listing.
       - RFR_CREDENTIALS_PATH: Path to service account JSON key, or None for Google Application Default Credentials (ADC).
    5. Ingestion State:
       - Disabled by default (ENABLE_REDDIT_RFR_INGESTION=false) until the user receives RFR approval
         and links their BigQuery subscriber dataset.
       - Verified demonstration data is served when disabled and ENABLE_DEMO_DATA_FALLBACK is True.
    6. Terms & Prohibitions:
       - AI Model Training Prohibition: Reddit data accessed through the RFR program must NOT be used
         for training artificial intelligence, foundation, or large language models without explicit,
         separate written consent from Reddit. FashionPulse AI strictly uses records for aggregate
         statistical frequency detection and velocity scoring.
       - Right to be Forgotten: Caches must honor user deletion requests within 48 hours.
    """

    def __init__(self):
        super().__init__(platform_name="reddit")
        self.is_enabled = bool(
            settings.ENABLE_REDDIT_RFR_INGESTION or getattr(settings, "ENABLE_LIVE_REDDIT_COLLECTOR", False)
        )
        self.project_id = settings.RFR_GCP_PROJECT_ID
        self.dataset_name = settings.RFR_DATASET_NAME
        self.table_name = settings.RFR_TABLE_NAME or "posts"
        self.credentials_path = settings.RFR_CREDENTIALS_PATH
        self.subreddits = settings.REDDIT_SUBREDDITS

    def get_missing_onboarding_details(self) -> List[str]:
        """Identifies which required BigQuery Analytics Hub configuration items are missing."""
        missing = []
        if not self.is_enabled:
            missing.append("ENABLE_REDDIT_RFR_INGESTION=false (Live ingestion disabled pending RFR approval)")
        if not self.project_id:
            missing.append("RFR_GCP_PROJECT_ID (Google Cloud Project ID linked to BigQuery Analytics Hub)")
        if not self.dataset_name:
            missing.append("RFR_DATASET_NAME (Linked BQAH subscriber dataset name in BigQuery)")
        return missing

    def validate_credentials(self) -> bool:
        """
        Verifies if RFR BigQuery ingestion is explicitly enabled and required GCP project / dataset
        parameters are populated.
        """
        if not self.is_enabled:
            return False
        return bool(self.project_id and self.dataset_name)

    async def verify_authorization(self) -> bool:
        """
        Verifies BigQuery connectivity and dataset authorization.
        Reports clear diagnostic status without assuming success or claiming unverified access.
        """
        if not self.is_enabled:
            self.record_error(
                "Reddit for Researchers (RFR) ingestion is disabled by default. Access requires official "
                "program approval via Google BigQuery Analytics Hub (BQAH). To enable once approved, configure "
                "RFR_GCP_PROJECT_ID, RFR_DATASET_NAME, and set ENABLE_REDDIT_RFR_INGESTION=true in .env."
            )
            return False

        missing = self.get_missing_onboarding_details()
        if missing:
            self.record_error(f"RFR BigQuery configuration incomplete: {'; '.join(missing)}")
            return False

        # Attempt BigQuery client initialization
        try:
            from google.cloud import bigquery
            from google.oauth2 import service_account
        except ImportError:
            self.record_error(
                "google-cloud-bigquery library is required for live RFR ingestion. "
                "Install with 'pip install google-cloud-bigquery' and configure Google Cloud ADC."
            )
            return False

        try:
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
                client = bigquery.Client(project=self.project_id, credentials=credentials)
            else:
                client = bigquery.Client(project=self.project_id)

            # Test minimal query against subscriber dataset table
            query = f"SELECT 1 FROM `{self.project_id}.{self.dataset_name}.{self.table_name}` LIMIT 1"
            query_job = client.query(query)
            # Run in executor to prevent blocking async loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, query_job.result)
            return True

        except Exception as ex:
            self.record_error(f"RFR BigQuery verification failed: {str(ex)}")
            return False

    async def fetch_recent_content(self, limit: int = 25) -> List[NormalizedContentItem]:
        """
        Fetches historical records from the approved RFR BigQuery subscriber dataset for configured subreddits.
        If disabled or unconfigured, serves verified demonstration data when demo fallback is enabled.
        """
        if not self.is_enabled or not self.validate_credentials():
            if settings.ENABLE_DEMO_DATA_FALLBACK:
                logger.info(
                    "Reddit for Researchers (RFR) live ingestion is disabled by default pending BigQuery Analytics "
                    "Hub approval; serving verified demonstration data."
                )
                all_demo = [item for item in get_demo_fashion_content() if item.platform == "reddit"]
                self.record_success(len(all_demo))
                return all_demo
            else:
                self.record_error("Reddit RFR ingestion is disabled and demo fallback is turned off.")
                return []

        # Live BigQuery ingestion path
        try:
            from google.cloud import bigquery
            from google.oauth2 import service_account
        except ImportError:
            self.record_error(
                "google-cloud-bigquery library is missing. Install with 'pip install google-cloud-bigquery'."
            )
            if settings.ENABLE_DEMO_DATA_FALLBACK:
                return [item for item in get_demo_fashion_content() if item.platform == "reddit"]
            return []

        try:
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
                client = bigquery.Client(project=self.project_id, credentials=credentials)
            else:
                client = bigquery.Client(project=self.project_id)

            subreddits_list = [s.lower() for s in self.subreddits]
            sql = f"""
                SELECT 
                    id, 
                    name, 
                    title, 
                    selftext, 
                    url, 
                    author, 
                    subreddit, 
                    score, 
                    upvote_ratio, 
                    num_comments, 
                    created_utc, 
                    permalink
                FROM `{self.project_id}.{self.dataset_name}.{self.table_name}`
                WHERE LOWER(subreddit) IN UNNEST(@subreddits)
                ORDER BY created_utc DESC
                LIMIT @limit
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ArrayQueryParameter("subreddits", "STRING", subreddits_list),
                    bigquery.ScalarQueryParameter("limit", "INT64", min(limit, 100))
                ]
            )

            loop = asyncio.get_event_loop()
            query_job = client.query(sql, job_config=job_config)
            rows = await loop.run_in_executor(None, lambda: list(query_job.result()))

            results: List[NormalizedContentItem] = []
            for row in rows:
                item = self._normalize_rfr_record(dict(row.items()))
                if item:
                    results.append(item)

            if results:
                self.record_success(len(results))
            return results

        except Exception as ex:
            msg = f"BigQuery query error on RFR dataset `{self.project_id}.{self.dataset_name}`: {str(ex)}"
            logger.error(msg)
            self.record_error(msg)
            if settings.ENABLE_DEMO_DATA_FALLBACK:
                return [item for item in get_demo_fashion_content() if item.platform == "reddit"]
            return []

    def _normalize_rfr_record(self, post: Dict[str, Any]) -> Optional[NormalizedContentItem]:
        """
        Normalizes an approved Reddit for Researchers BigQuery record into the FashionPulse
        NormalizedContentItem schema without violating RFR terms (preserving author hashing).
        """
        post_id = post.get("id") or post.get("name")
        if not post_id:
            return None

        # Strip prefix if 'name' (e.g. 't3_123') was provided
        if str(post_id).startswith("t3_"):
            clean_id = str(post_id)[3:]
        else:
            clean_id = str(post_id)

        title = str(post.get("title") or "")
        selftext = str(post.get("selftext") or "")
        full_text = f"{title}\n{selftext}".strip()

        raw_created = post.get("created_utc")
        if isinstance(raw_created, datetime):
            published_at = raw_created if raw_created.tzinfo else raw_created.replace(tzinfo=timezone.utc)
        elif isinstance(raw_created, (int, float)):
            published_at = datetime.fromtimestamp(raw_created, tz=timezone.utc)
        elif isinstance(raw_created, str):
            try:
                published_at = datetime.fromisoformat(raw_created.replace("Z", "+00:00"))
            except Exception:
                published_at = datetime.now(timezone.utc)
        else:
            published_at = datetime.now(timezone.utc)

        raw_permalink = post.get("permalink") or f"/r/{post.get('subreddit', 'fashion')}/comments/{clean_id}"
        permalink = raw_permalink if str(raw_permalink).startswith("http") else f"https://reddit.com{raw_permalink}"

        # Score and engagement metrics
        score = int(post.get("score") or 0)
        upvote_ratio = float(post.get("upvote_ratio") or 1.0)
        num_comments = int(post.get("num_comments") or 0)

        # Author identifier: RFR provides hashed or masked IDs; preserve as provided to avoid de-anonymization
        author_id = str(post.get("author") or "rfr_anonymized_user")

        return NormalizedContentItem(
            platform="reddit",
            external_id=f"reddit_{clean_id}",
            title=title,
            content_text=full_text,
            author_id=author_id,
            permalink=permalink,
            published_at=published_at,
            raw_metrics={
                "score": score,
                "upvote_ratio": upvote_ratio,
                "num_comments": num_comments
            },
            is_demo=False
        )

    def _normalize_reddit_post(self, post: Dict[str, Any]) -> Optional[NormalizedContentItem]:
        """Backward-compatible alias for unit test normalization checks."""
        return self._normalize_rfr_record(post)


# Provide both names for clean compatibility across services and endpoints
RedditConnector = RedditRFRConnector
reddit_connector = RedditRFRConnector()
