import asyncio
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger("mediscan.integrations")

class BaseIntegration:
    """Base class for all external research data integrations."""
    
    def __init__(self, source_name: str, base_url: str, timeout_seconds: float = 12.0, max_retries: int = 2):
        self.source_name = source_name
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET"
    ) -> Optional[Dict[str, Any]]:
        """Execute an asynchronous HTTP request with retries and exponential backoff."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}" if endpoint else self.base_url
        
        for attempt in range(1, self.max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, params=params, headers=headers)
                    elif method.upper() == "POST":
                        response = await client.post(url, json=params, headers=headers)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 429:
                        # Rate limit reached
                        retry_after = int(response.headers.get("Retry-After", 2))
                        logger.warning(f"[{self.source_name}] Rate limited (429). Backing off for {retry_after}s.")
                        if attempt <= self.max_retries:
                            await asyncio.sleep(retry_after)
                            continue
                    else:
                        logger.warning(f"[{self.source_name}] HTTP {response.status_code} for {url}")
                        return None
            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.warning(f"[{self.source_name}] Request error on attempt {attempt}/{self.max_retries + 1}: {str(e)}")
                if attempt <= self.max_retries:
                    await asyncio.sleep(1.0 * attempt)
                    continue
                return None
            except Exception as e:
                logger.error(f"[{self.source_name}] Unexpected error: {str(e)}")
                return None
        return None
