import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.schemas.nemotron import NemotronPayload, NemotronTrendItem, NemotronHandoffResponse


class BaseNemotronAdapter(ABC):
    """Abstract interface for Nemotron model handoff integration."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Checks if live endpoint and credentials are configured."""
        pass

    @abstractmethod
    async def send_payload(self, payload: NemotronPayload) -> NemotronHandoffResponse:
        """Sends payload to Nemotron service."""
        pass


class NemotronServiceAdapter(BaseNemotronAdapter):
    """
    Production adapter for NVIDIA Nemotron LLM endpoint.
    Communicates via standard OpenAI-compatible or NVIDIA NIM inference API.
    """

    def __init__(self):
        self.endpoint_url = settings.NEMOTRON_ENDPOINT_URL
        self.api_key = settings.NEMOTRON_API_KEY
        self.model_name = settings.NEMOTRON_MODEL_NAME
        self.timeout = settings.NEMOTRON_TIMEOUT_SECONDS

    def is_configured(self) -> bool:
        return bool(self.endpoint_url and len(self.endpoint_url) > 8)

    async def send_payload(self, payload: NemotronPayload) -> NemotronHandoffResponse:
        now = datetime.now(timezone.utc)
        handoff_id = f"handoff_{int(now.timestamp())}"

        if not self.is_configured():
            logger.warning("Nemotron handoff aborted: Nemotron not configured.")
            return NemotronHandoffResponse(
                handoff_id=handoff_id,
                status="failed",
                endpoint_used=None,
                status_code=None,
                response_summary=None,
                error_detail="Nemotron not configured: NEMOTRON_ENDPOINT_URL is missing in environment.",
                timestamp=now
            )

        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Standard prompt wrapping structured fashion trend payload for Nemotron intelligence
        request_body = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "You are NVIDIA Nemotron Fashion Intelligence Model. Analyze the provided multi-platform social media trend payload and provide strategic fashion retail predictions and aesthetic lifecycle commentary."
                },
                {
                    "role": "user",
                    "content": payload.model_dump_json()
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Dispatching payload to Nemotron at {self.endpoint_url}...")
                resp = await client.post(self.endpoint_url, json=request_body, headers=headers)
                
                if resp.status_code in [200, 201]:
                    logger.info("Nemotron handoff succeeded.")
                    return NemotronHandoffResponse(
                        handoff_id=handoff_id,
                        status="sent",
                        endpoint_used=self.endpoint_url,
                        status_code=resp.status_code,
                        response_summary=resp.text[:300],
                        error_detail=None,
                        timestamp=now
                    )
                else:
                    logger.error(f"Nemotron handoff failed with status {resp.status_code}: {resp.text}")
                    return NemotronHandoffResponse(
                        handoff_id=handoff_id,
                        status="failed",
                        endpoint_used=self.endpoint_url,
                        status_code=resp.status_code,
                        response_summary=None,
                        error_detail=f"Nemotron HTTP Error {resp.status_code}: {resp.text[:200]}",
                        timestamp=now
                    )

        except Exception as ex:
            logger.error(f"Nemotron handoff exception: {str(ex)}")
            return NemotronHandoffResponse(
                handoff_id=handoff_id,
                status="failed",
                endpoint_used=self.endpoint_url,
                status_code=None,
                response_summary=None,
                error_detail=f"Connection failure: {str(ex)}",
                timestamp=now
            )


class MockNemotronAdapter(BaseNemotronAdapter):
    """Mock adapter used strictly for automated tests and offline verification."""

    def __init__(self, simulate_success: bool = True):
        self.simulate_success = simulate_success

    def is_configured(self) -> bool:
        return True

    async def send_payload(self, payload: NemotronPayload) -> NemotronHandoffResponse:
        now = datetime.now(timezone.utc)
        handoff_id = f"mock_handoff_{int(now.timestamp())}"
        
        if self.simulate_success:
            return NemotronHandoffResponse(
                handoff_id=handoff_id,
                status="sent",
                endpoint_used="https://mock-nemotron-inference.internal/v1/chat/completions",
                status_code=200,
                response_summary="[MOCK INFERENCE] Nemotron successfully generated fashion trend analysis.",
                error_detail=None,
                timestamp=now
            )
        else:
            return NemotronHandoffResponse(
                handoff_id=handoff_id,
                status="failed",
                endpoint_used="https://mock-nemotron-inference.internal/v1/chat/completions",
                status_code=503,
                response_summary=None,
                error_detail="[MOCK ERROR] Service temporarily unavailable.",
                timestamp=now
            )


nemotron_adapter = NemotronServiceAdapter()
