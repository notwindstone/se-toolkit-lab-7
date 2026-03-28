"""
Service layer for the LMS Bot.

Services handle external communication (API calls, LLM, etc.).
"""

from services.api_client import lms_client, LMSAPIClient, LMSAPIError

__all__ = ["lms_client", "LMSAPIClient", "LMSAPIError"]
