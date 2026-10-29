import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Set
import httpx
from app.connectors.base import BaseSocialConnector, NormalizedContentItem
from app.connectors.mock_data import get_demo_fashion_content
from app.core.config import settings
from app.core.logging import logger


class YouTubeConnector(BaseSocialConnector):
    """
    YouTube Data API v3 connector.
    
    API Quota Model (Google Cloud Quotas & System Limits):
    - Dedicated Search Quota Bucket: Google allocates a default limit of 100 'search.list' calls
      per day per project. Each search query costs 1 unit from this dedicated search bucket.
    - General Quota Pool: Google allocates 10,000 units per day for standard endpoints.
      Each 'videos.list' call costs 1 unit from this general pool and can batch up to 50 video IDs.
    - Two-Phase Optimization:
      1. Search Phase: Strictly limits queries to the primary search terms (consuming 1 call
         from the 100 search bucket per term).
      2. Batch Hydration Phase: Batches up to 50 discovered video IDs into a single 'videos.list'
         call (consuming only 1 unit from the 10,000 general pool).
    - Quota Preservation: Authorization verification deliberately calls 'videos.list?chart=mostPopular'
      (1 general unit), completely preserving the 100-call search bucket for actual data collection.
    - Reset Schedule: Quotas reset daily at midnight Pacific Time (PT).
    - Audit & Extensions: Exceeding 100 search calls/day requires submitting the YouTube API Services
      Audit and Quota Extension Form via Google Cloud Console.
    """

    def __init__(self):
        super().__init__(platform_name="youtube")
        self.search_terms = settings.YOUTUBE_SEARCH_TERMS
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.seen_video_ids: Set[str] = set()

    @property
    def api_key(self) -> Optional[str]:
        return settings.YOUTUBE_API_KEY

    def validate_credentials(self) -> bool:
        """Verifies if YouTube API key is provided and meets basic format requirements."""
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    async def verify_authorization(self) -> bool:
        """
        Verifies API key using a minimal 1-quota request from the 10,000 general pool
        ('videos.list?chart=mostPopular&maxResults=1&part=id') rather than 'search.list',
        preserving all 100 daily search calls in the dedicated search bucket.
        """
        if not self.validate_credentials():
            self.is_authorized = False
            return False
        url = f"{self.base_url}/videos?part=id&chart=mostPopular&maxResults=1&key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    self.is_authorized = True
                    self.last_error_message = None
                    return True
                else:
                    self.is_authorized = False
                    err = resp.json().get("error", {})
                    errors_list = err.get("errors", [])
                    reason = errors_list[0].get("reason", "unknown") if errors_list else "unknown"
                    if reason == "quotaExceeded":
                        detail = "YouTube API quota exceeded (10,000 daily general units exhausted; resets midnight PT)."
                    elif reason in ["keyInvalid", "forbidden"]:
                        detail = f"YouTube API Key invalid or restricted: {err.get('message', resp.text)}"
                    else:
                        detail = f"YouTube API validation failed ({reason}): {err.get('message', resp.text)}"
                    self.record_error(detail)
                    return False
        except Exception as e:
            self.is_authorized = False
            self.record_error(f"YouTube API connection error: {str(e)}")
            return False

    async def fetch_recent_content(self, limit: int = 25) -> List[NormalizedContentItem]:
        """
        Executes search and batch details requests.
        Serves verified demo data if API key is not configured and fallback is enabled.
        """
        if not self.validate_credentials():
            if settings.ENABLE_DEMO_DATA_FALLBACK:
                logger.info("YouTube credentials not configured; serving verified demo data.")
                all_demo = [item for item in get_demo_fashion_content() if item.platform == "youtube"]
                self.record_success(len(all_demo), is_demo=True)
                return all_demo
            else:
                self.record_error("YouTube API key is not configured in environment.")
                return []

        results: List[NormalizedContentItem] = []
        video_ids_to_fetch: List[str] = []

        async with httpx.AsyncClient(timeout=20.0) as client:
            # 1. Search for recent videos across all configured fashion queries
            seen_in_call: Set[str] = set()
            for term in self.search_terms:
                try:
                    search_url = (
                        f"{self.base_url}/search"
                        f"?part=id&type=video&q={term}&order=date"
                        f"&maxResults={min(limit, 15)}&key={self.api_key}"
                    )
                    resp = await client.get(search_url)
                    if resp.status_code == 403:
                        err = resp.json().get("error", {})
                        errors_list = err.get("errors", [])
                        reason = errors_list[0].get("reason", "") if errors_list else ""
                        if reason == "quotaExceeded":
                            self.record_error(
                                "YouTube Search quota exceeded (dedicated 100 search queries/day bucket exhausted; "
                                "resets midnight PT). Apply for a quota extension in Google Cloud Console."
                            )
                        else:
                            self.record_error(f"YouTube Search forbidden ({reason}): {err.get('message', resp.text)}")
                        break
                    
                    if resp.status_code == 200:
                        items = resp.json().get("items", [])
                        for item in items:
                            vid_id = item.get("id", {}).get("videoId")
                            if vid_id and vid_id not in seen_in_call and vid_id not in self.seen_video_ids:
                                video_ids_to_fetch.append(vid_id)
                                seen_in_call.add(vid_id)
                                self.seen_video_ids.add(vid_id)

                except Exception as ex:
                    logger.warning(f"Error querying YouTube for term '{term}': {str(ex)}")

            if not video_ids_to_fetch:
                return results

            # 2. Batch request video details & statistics (up to 50 per batch)
            chunks = [video_ids_to_fetch[i:i + 50] for i in range(0, len(video_ids_to_fetch), 50)]
            for chunk in chunks:
                try:
                    ids_str = ",".join(chunk)
                    detail_url = (
                        f"{self.base_url}/videos"
                        f"?part=snippet,statistics&id={ids_str}&key={self.api_key}"
                    )
                    d_resp = await client.get(detail_url)
                    if d_resp.status_code == 200:
                        videos = d_resp.json().get("items", [])
                        for v in videos:
                            norm = self._normalize_youtube_video(v)
                            if norm:
                                results.append(norm)
                except Exception as ex:
                    logger.warning(f"Error fetching batch video details: {str(ex)}")

        if results:
            self.record_success(len(results), is_demo=False)
            self.is_authorized = True
        return results

    def _normalize_youtube_video(self, v: Dict[str, Any]) -> Optional[NormalizedContentItem]:
        """Normalizes YouTube Video JSON object into schema."""
        vid_id = v.get("id")
        if not vid_id:
            return None

        snippet = v.get("snippet", {})
        statistics = v.get("statistics", {})

        title = snippet.get("title", "")
        description = snippet.get("description", "")
        published_str = snippet.get("publishedAt")
        try:
            published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00")) if published_str else datetime.now(timezone.utc)
        except Exception:
            published_at = datetime.now(timezone.utc)

        full_text = f"{title}\n{description}".strip()

        return NormalizedContentItem(
            platform="youtube",
            external_id=f"yt_{vid_id}",
            title=title,
            content_text=full_text,
            author_id=snippet.get("channelTitle", "unknown_channel"),
            permalink=f"https://www.youtube.com/watch?v={vid_id}",
            published_at=published_at,
            raw_metrics={
                "views": int(statistics.get("viewCount", 0)),
                "likes": int(statistics.get("likeCount", 0)),
                "comments": int(statistics.get("commentCount", 0))
            },
            is_demo=False
        )


youtube_connector = YouTubeConnector()
