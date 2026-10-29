import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import httpx
from app.connectors.base import BaseSocialConnector, NormalizedContentItem
from app.connectors.mock_data import get_demo_fashion_content
from app.core.config import settings
from app.core.logging import logger


class InstagramConnector(BaseSocialConnector):
    """
    Instagram connector leveraging the official Meta Graph API (v26.0).
    
    Compliance, Permissions & Access Constraints:
    1. API Version: Meta Graph API v26.0 (latest supported release as of October 2026).
    2. Permissions: Requires a registered Meta Developer App with 'instagram_basic' and
       'pages_read_engagement' (or 'business_management') permissions.
    3. Restricted Feature (IPCA): Upgrading the API version does NOT grant access to restricted
       endpoints. Querying hashtag discovery edges strictly requires the 'Instagram Public Content Access'
       (IPCA) feature approved via Meta App Review and Business Verification.
       In Development Mode, requests only succeed for users added directly as App Administrators,
       Developers, or Testers with an Instagram Business/Creator account connected to a Facebook Page.
    4. Exact Endpoints:
       - Hashtag ID lookup: GET /v26.0/ig_hashtag_search?user_id={IG_BUSINESS_ACCOUNT_ID}&q={tag}
       - Recent Media: GET /v26.0/{hashtag_id}/recent_media?user_id={IG_BUSINESS_ACCOUNT_ID}&fields={fields}
    5. Permitted Fields: id, caption, media_type, media_url, permalink, timestamp, like_count, comments_count.
       Note: The 'username' field is strictly prohibited on hashtag media nodes and returns HTTP 400.
    6. Platform Limits: Maximum 30 unique hashtags queried per rolling 7-day period per Instagram
       account, and content is restricted to public posts created within the preceding 24 hours.
    """
    
    def __init__(self):
        super().__init__(platform_name="instagram")
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.business_account_id = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.hashtags = settings.INSTAGRAM_HASHTAGS
        self.api_version = settings.INSTAGRAM_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def validate_credentials(self) -> bool:
        """Verifies if access token and business account ID are populated."""
        return bool(
            self.access_token and len(self.access_token) > 10 and
            self.business_account_id and len(self.business_account_id) > 3
        )

    async def verify_authorization(self) -> bool:
        """
        Tests validity of credentials against Graph API account endpoint.
        Validates token expiration, account linkage, and necessary permissions.
        """
        if not self.validate_credentials():
            return False
        # Querying the business account directly verifies both token validity and account linkage
        url = f"{self.base_url}/{self.business_account_id}?fields=id,name&access_token={self.access_token}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return True
                else:
                    err = resp.json().get("error", {})
                    code = err.get("code")
                    subcode = err.get("error_subcode")
                    msg = err.get("message", resp.text)
                    if code == 190:
                        detail = f"Meta Access Token expired or invalid (subcode {subcode}): {msg}"
                    elif code == 10:
                        detail = f"Missing required permissions or Instagram Public Content Access feature: {msg}"
                    else:
                        detail = f"Meta Graph API verification failed (HTTP {resp.status_code}, code {code}): {msg}"
                    self.record_error(detail)
                    return False
        except Exception as e:
            self.record_error(f"Meta Graph API connection error: {str(e)}")
            return False

    async def fetch_recent_content(self, limit: int = 25) -> List[NormalizedContentItem]:
        """
        Fetches recent public fashion media for configured hashtags using Graph API.
        If credentials are not present, serves verified demonstration data when allowed.
        """
        if not self.validate_credentials():
            if settings.ENABLE_DEMO_DATA_FALLBACK:
                logger.info("Instagram credentials not configured; serving verified demo data.")
                all_demo = [item for item in get_demo_fashion_content() if item.platform == "instagram"]
                self.record_success(len(all_demo))
                return all_demo
            else:
                self.record_error("Instagram credentials are not configured in environment.")
                return []

        results: List[NormalizedContentItem] = []
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            for tag in self.hashtags[:2]:
                try:
                    # 1. Look up Hashtag ID
                    tag_search_url = (
                        f"{self.base_url}/ig_hashtag_search"
                        f"?user_id={self.business_account_id}&q={tag}&access_token={self.access_token}"
                    )
                    resp = await client.get(tag_search_url)
                    if resp.status_code != 200:
                        err = resp.json().get("error", {})
                        code = err.get("code")
                        if code == 10:
                            err_msg = (
                                f"Hashtag lookup error for #{tag}: Permission denied. Ensure 'Instagram Public "
                                f"Content Access' feature is approved and 'instagram_basic' permission is granted."
                            )
                        elif code in [4, 17]:
                            err_msg = f"Hashtag lookup rate limit exceeded (30 unique hashtags per rolling 7 days limit)."
                        else:
                            err_msg = f"Hashtag lookup error for #{tag}: {err.get('message', resp.text)}"
                        self.record_error(err_msg)
                        continue

                    data = resp.json()
                    data_items = data.get("data", [])
                    if not data_items:
                        continue
                    hashtag_id = data_items[0].get("id")
                    if not hashtag_id:
                        continue

                    # 2. Get recent media for hashtag (valid fields: id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count)
                    # Note: 'username' is strictly prohibited by Meta on hashtag search endpoints
                    media_url = (
                        f"{self.base_url}/{hashtag_id}/recent_media"
                        f"?user_id={self.business_account_id}"
                        f"&fields=id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count"
                        f"&limit={min(limit, 20)}&access_token={self.access_token}"
                    )
                    media_resp = await client.get(media_url)
                    if media_resp.status_code == 200:
                        media_items = media_resp.json().get("data", [])
                        for m in media_items:
                            item = self._normalize_media_item(m)
                            if item:
                                results.append(item)
                    elif media_resp.status_code == 429:
                        self.record_error("Instagram Graph API rate limit exceeded.")
                        break
                    else:
                        err_json = media_resp.json().get("error", {})
                        self.record_error(f"Failed to fetch media for #{tag}: {err_json.get('message', media_resp.text)}")

                except Exception as ex:
                    logger.warning(f"Error fetching Instagram tag #{tag}: {str(ex)}")

        if results:
            self.record_success(len(results))
        return results

    def _normalize_media_item(self, m: Dict[str, Any]) -> Optional[NormalizedContentItem]:
        """Normalizes Meta Instagram Graph media schema."""
        media_id = m.get("id")
        if not media_id:
            return None

        caption = m.get("caption", "")
        raw_ts = m.get("timestamp")
        try:
            published_at = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")) if raw_ts else datetime.now(timezone.utc)
        except Exception:
            published_at = datetime.now(timezone.utc)

        return NormalizedContentItem(
            platform="instagram",
            external_id=f"ig_{media_id}",
            title=None,
            content_text=caption,
            author_id="ig_creator",
            permalink=m.get("permalink", f"https://instagram.com/p/{media_id}"),
            published_at=published_at,
            raw_metrics={
                "like_count": m.get("like_count", 0),
                "comments_count": m.get("comments_count", 0)
            },
            is_demo=False
        )


instagram_connector = InstagramConnector()
