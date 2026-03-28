"""
LLM client for tool-based intent routing.

Wraps the LLM API with tool calling support. The client:
1. Sends user message + tool definitions to LLM
2. Parses tool calls from response
3. Executes tools and feeds results back
4. Returns final summary from LLM
"""

import json
import sys
from typing import Any, Callable

import httpx

from config import settings

# Tool definitions for all 9 backend endpoints
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks from the backend. Use this when user asks about available labs, what labs exist, or wants to see the catalog.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their group assignments. Use this when user asks about students, enrollment, or group membership.",
            "parameters": {
                "type": "object",
                "properties": {
                    "group": {"type": "string", "description": "Optional: filter by group name, e.g. 'A', 'B'"}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a lab. Use when user asks about score distribution or how students performed in buckets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab. Use when user asks about scores, pass rates, task performance, or which tasks are hardest.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab. Use when user asks about submission timeline, when students submitted, or activity over time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance scores and student counts for a lab. Use when user asks about group comparison, which group is best, or group performance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab. Use when user asks about top students, leaderboard, best performers, or who did best.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return, default 5"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab. Use when user asks about completion rate, how many finished, or percentage completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker. Use when user asks to refresh data, sync, or update the backend.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM
SYSTEM_PROMPT = """You are an assistant for a Learning Management System (LMS). You have access to backend data through tools.

When a user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Once you have the data, summarize it clearly for the user
4. Include specific numbers, lab names, and task names in your answer

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students and groups
- get_scores: Score distribution for a lab
- get_pass_rates: Per-task pass rates for a lab
- get_timeline: Submissions per day for a lab
- get_groups: Per-group performance for a lab
- get_top_learners: Top N students for a lab
- get_completion_rate: Completion percentage for a lab
- trigger_sync: Refresh data from autochecker

For multi-step questions (e.g., "which lab has the lowest pass rate?"), you may need to call multiple tools:
1. First call get_items to get all labs
2. Then call get_pass_rates for each lab
3. Compare the results and provide the answer

Always call tools when you need data. Don't guess or make up numbers.
If the user's message is a greeting or unclear, respond helpfully without calling tools.
"""


class LLMClient:
    """Client for LLM tool calling."""

    def __init__(self):
        self.base_url = settings.llm_api_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_api_model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60.0,
        )

        # Tool registry: name -> callable
        self._tools: dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable) -> None:
        """Register a tool function by name."""
        self._tools[name] = func

    def _call_llm(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """Call the LLM API."""
        response = self._client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "tools": TOOLS,
                "tool_choice": "auto",
            },
        )
        response.raise_for_status()
        return response.json()

    def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a registered tool function."""
        if name not in self._tools:
            return {"error": f"Unknown tool: {name}"}
        try:
            result = self._tools[name](**arguments)
            return result
        except Exception as e:
            return {"error": str(e)}

    def route(self, user_message: str, debug: bool = False) -> str:
        """
        Route a user message through the LLM tool-calling loop.

        Returns the final response string.
        """
        # Initialize conversation
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call LLM
            response = self._call_llm(messages)
            choice = response["choices"][0]["message"]

            # Check for tool calls
            tool_calls = choice.get("tool_calls", [])

            if not tool_calls:
                # No tool calls - LLM is done, return the response
                return choice.get("content", "I don't have enough information to answer that.")

            # Execute tool calls and collect results
            tool_results = []
            for tool_call in tool_calls:
                function = tool_call["function"]
                name = function["name"]
                arguments = json.loads(function["arguments"])

                if debug:
                    print(f"[tool] LLM called: {name}({arguments})", file=sys.stderr)

                # Execute the tool
                result = self._execute_tool(name, arguments)

                if debug:
                    print(f"[tool] Result: {json.dumps(result, default=str)[:100]}...", file=sys.stderr)

                # Add tool result to messages
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result, default=str),
                })

            # Feed tool results back to LLM
            messages.append(choice)
            messages.extend(tool_results)

            if debug:
                print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)

        # Max iterations reached
        return "I'm having trouble processing this request. Please try rephrasing."


# Global client instance
llm_client = LLMClient()


# Tool implementations - these wrap the API client
from services.api_client import lms_client


def tool_get_items() -> list[dict]:
    """Get all items (labs and tasks)."""
    return lms_client.get_items()


def tool_get_learners(group: str = None) -> list[dict]:
    """Get enrolled learners."""
    items = lms_client.get_items()  # Use existing client
    # Actually call the learners endpoint
    import httpx
    from config import settings
    with httpx.Client(
        base_url=settings.lms_api_base_url,
        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
        timeout=10.0,
    ) as client:
        response = client.get("/learners/", params={"group": group} if group else {})
        response.raise_for_status()
        return response.json()


def tool_get_scores(lab: str) -> list[dict]:
    """Get score distribution for a lab."""
    import httpx
    from config import settings
    with httpx.Client(
        base_url=settings.lms_api_base_url,
        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
        timeout=10.0,
    ) as client:
        response = client.get("/analytics/scores", params={"lab": lab})
        response.raise_for_status()
        return response.json()


def tool_get_pass_rates(lab: str) -> list[dict]:
    """Get pass rates for a lab."""
    return lms_client.get_pass_rates(lab)


def tool_get_timeline(lab: str) -> list[dict]:
    """Get timeline for a lab."""
    import httpx
    from config import settings
    with httpx.Client(
        base_url=settings.lms_api_base_url,
        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
        timeout=10.0,
    ) as client:
        response = client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()


def tool_get_groups(lab: str) -> list[dict]:
    """Get group performance for a lab."""
    import httpx
    from config import settings
    with httpx.Client(
        base_url=settings.lms_api_base_url,
        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
        timeout=10.0,
    ) as client:
        response = client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()


def tool_get_top_learners(lab: str, limit: int = 5) -> list[dict]:
    """Get top learners for a lab."""
    import httpx
    from config import settings
    with httpx.Client(
        base_url=settings.lms_api_base_url,
        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
        timeout=10.0,
    ) as client:
        response = client.get("/analytics/top-learners", params={"lab": lab, "limit": limit})
        response.raise_for_status()
        return response.json()


def tool_get_completion_rate(lab: str) -> dict:
    """Get completion rate for a lab."""
    import httpx
    from config import settings
    with httpx.Client(
        base_url=settings.lms_api_base_url,
        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
        timeout=10.0,
    ) as client:
        response = client.get("/analytics/completion-rate", params={"lab": lab})
        response.raise_for_status()
        return response.json()


def tool_trigger_sync() -> dict:
    """Trigger ETL sync."""
    import httpx
    from config import settings
    with httpx.Client(
        base_url=settings.lms_api_base_url,
        headers={"Authorization": f"Bearer {settings.lms_api_key}"},
        timeout=10.0,
    ) as client:
        response = client.post("/pipeline/sync", json={})
        response.raise_for_status()
        return response.json()


# Register all tools
llm_client.register_tool("get_items", tool_get_items)
llm_client.register_tool("get_learners", tool_get_learners)
llm_client.register_tool("get_scores", tool_get_scores)
llm_client.register_tool("get_pass_rates", tool_get_pass_rates)
llm_client.register_tool("get_timeline", tool_get_timeline)
llm_client.register_tool("get_groups", tool_get_groups)
llm_client.register_tool("get_top_learners", tool_get_top_learners)
llm_client.register_tool("get_completion_rate", tool_get_completion_rate)
llm_client.register_tool("trigger_sync", tool_trigger_sync)
