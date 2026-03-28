"""
Intent router for natural language queries.

Uses LLM tool calling to route user queries to the appropriate backend tools.
No regex or keyword matching - the LLM decides which tool to call.
"""

from services.llm_client import llm_client


def handle_natural_language(message: str, debug: bool = True) -> str:
    """
    Process a natural language message through the LLM intent router.

    Args:
        message: The user's message (plain text)
        debug: Whether to print debug info to stderr

    Returns:
        The LLM's response string
    """
    try:
        return llm_client.route(message, debug=debug)
    except Exception as e:
        # Handle LLM errors gracefully
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            return "LLM authentication error. The API token may have expired."
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            return "LLM service is unavailable. Please try again later."
        else:
            return f"LLM error: {error_msg}"
