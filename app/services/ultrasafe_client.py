from typing import Dict, Any, List, Optional
import httpx
import logging
import structlog
from ..core.config import settings

logger = structlog.get_logger()

class UltraSafeClient:
    def __init__(self):
        self.base_url = settings.ULTRASAFE_API_URL
        self.api_key = settings.ULTRASAFE_API_KEY
        self.timeout = settings.ULTRASAFE_TIMEOUT
        self.max_retries = settings.ULTRASAFE_MAX_RETRIES
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make request to UltraSafe API."""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        json=data,
                        headers=self.headers
                    )
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPError as e:
                logger.error(
                    "ultrasafe_api_error",
                    endpoint=endpoint,
                    error=str(e),
                    attempt=attempt + 1
                )
                if attempt == self.max_retries - 1:
                    raise
            except Exception as e:
                logger.error(
                    "ultrasafe_api_error",
                    endpoint=endpoint,
                    error=str(e),
                    attempt=attempt + 1
                )
                if attempt == self.max_retries - 1:
                    raise

    async def classify_text(
        self,
        text: str,
        categories: List[str],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Classify text into categories."""
        data = {
            "text": text,
            "categories": categories
        }
        if context:
            data["context"] = context

        return await self._make_request("POST", "classify", data)

    async def extract_entities(
        self,
        text: str,
        entity_types: List[str],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract entities from text."""
        data = {
            "text": text,
            "entity_types": entity_types
        }
        if context:
            data["context"] = context

        return await self._make_request("POST", "extract-entities", data)

    async def summarize_text(
        self,
        text: str,
        max_length: int,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Summarize text."""
        data = {
            "text": text,
            "max_length": max_length
        }
        if context:
            data["context"] = context

        return await self._make_request("POST", "summarize", data)

    async def analyze_sentiment(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        data = {"text": text}
        if context:
            data["context"] = context

        return await self._make_request("POST", "analyze-sentiment", data)

# Create singleton instance
ultrasafe_client = UltraSafeClient() 