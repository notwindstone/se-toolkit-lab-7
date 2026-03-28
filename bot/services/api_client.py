"""
API client for the LMS backend.

Provides methods to fetch labs, pass rates, and health status.
All methods return typed data or raise exceptions with user-friendly messages.
"""

import httpx
from typing import Any

from config import settings


class LMSAPIError(Exception):
    """Base exception for LMS API errors."""

    pass


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self):
        self.base_url = settings.lms_api_base_url
        self.api_key = settings.lms_api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def get_items(self) -> list[dict[str, Any]]:
        """Fetch all items (labs and tasks) from the backend."""
        try:
            response = self._client.get("/items/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise LMSAPIError(f"HTTP {e.response.status_code}: {e.response.reason_phrase}")
        except httpx.ConnectError as e:
            raise LMSAPIError(f"connection refused ({self.base_url}). Check that the services are running.")
        except httpx.HTTPError as e:
            raise LMSAPIError(f"HTTP error: {str(e)}")

    def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Fetch pass rates for a specific lab."""
        try:
            response = self._client.get("/analytics/pass-rates", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise LMSAPIError(f"Lab '{lab}' not found")
            raise LMSAPIError(f"HTTP {e.response.status_code}: {e.response.reason_phrase}")
        except httpx.ConnectError as e:
            raise LMSAPIError(f"connection refused ({self.base_url}). Check that the services are running.")
        except httpx.HTTPError as e:
            raise LMSAPIError(f"HTTP error: {str(e)}")

    def get_item_count(self) -> int:
        """Get the number of items in the backend (for health check)."""
        items = self.get_items()
        return len(items)


# Global client instance
lms_client = LMSAPIClient()
