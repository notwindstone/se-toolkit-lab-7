# Intent-Based Natural Language Routing

Make the bot understand plain text. The user types a question, and the bot uses an LLM to decide what data to fetch and how to answer.

## Requirements targeted

- **P1.1** Natural language intent routing — plain text interpreted by LLM
- **P1.2** All 9 backend endpoints wrapped as LLM tools
- **P1.3** Inline keyboard buttons
- **P1.4** Multi-step reasoning (chaining API calls)

## What you will build

An intent router: plain text → LLM with tool definitions → API calls → formatted response.

```terminal
$ python bot/bot.py --test "which lab has the lowest pass rate?"
Based on the data, Lab 03 has the lowest average pass rate at 62.3%.
- Backend API: 58.1% (145 attempts)
- Security Hardening: 66.5% (132 attempts)
```

This builds on Lab 6 — same tool use pattern, but embedded in a user-facing bot.

## How it works

```
User: "which lab has the worst results?"
  → sends message + tool definitions to LLM
  → LLM decides: call get_pass_rates for each lab
  → bot executes the API calls
  → LLM summarizes
  → bot sends response
```

## Required tools

All 9 backend endpoints as LLM tools:

| Tool | Endpoint | LLM description |
|------|----------|----------------|
| `get_items` | `GET /items/` | List of labs and tasks |
| `get_learners` | `GET /learners/` | Enrolled students and groups |
| `get_scores` | `GET /analytics/scores?lab=` | Score distribution (4 buckets) |
| `get_pass_rates` | `GET /analytics/pass-rates?lab=` | Per-task averages and attempt counts |
| `get_timeline` | `GET /analytics/timeline?lab=` | Submissions per day |
| `get_groups` | `GET /analytics/groups?lab=` | Per-group scores and student counts |
| `get_top_learners` | `GET /analytics/top-learners?lab=&limit=` | Top N learners by score |
| `get_completion_rate` | `GET /analytics/completion-rate?lab=` | Completion rate percentage |
| `trigger_sync` | `POST /pipeline/sync` | Refresh data from autochecker |

Example schema:

```python
{
    "type": "function",
    "function": {
        "name": "get_pass_rates",
        "description": "Get per-task average scores and attempt counts for a lab",
        "parameters": {
            "type": "object",
            "properties": {
                "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
            },
            "required": ["lab"],
        },
    },
}
```

## Scenarios

**Single API call:**

| Message | Behavior |
|---------|----------|
| "what labs are available?" | `get_items` → list labs |
| "show me scores for lab 4" | `get_pass_rates(lab="lab-04")` → format |
| "who are the top 5 students?" | `get_top_learners(limit=5)` → leaderboard |
| "which group is best in lab 3?" | `get_groups(lab="lab-03")` → rank |

**Multi-step:**

| Message | Behavior |
|---------|----------|
| "which lab has the lowest pass rate?" | `get_items` → `get_pass_rates` per lab → compare |
| "compare group A and group B" | `get_groups` → filter → compare |

**Fallback:**

| Message | Behavior |
|---------|----------|
| "hello" | Greeting + capabilities hint |
| "asdfgh" | "I didn't understand. Here's what I can do..." |
| "lab 4" | "What about lab 4? I can show scores, pass rates..." |

## Inline buttons

Add keyboard buttons so users can discover actions without typing.

## Acceptance criteria

- [ ] `--test "what labs are available"` returns non-empty answer (at least 20 chars).
- [ ] `--test "which lab has the lowest pass rate"` mentions a specific lab.
- [ ] `--test "asdfgh"` returns a helpful message, no crash.
- [ ] Source code contains keyboard/button setup.
- [ ] Source code defines at least 9 tool/function schemas.
- [ ] Git workflow followed.

## Agent instructions

Follow these to maximize learning. Do not skip.

**Engage before explaining.** Ask first, let the student think, then fill gaps.

> Ask: "Do you know how LLM function calling works? How does the LLM decide which tool to call?" If not, explain with one example: one tool, one message, the full loop (user → LLM → tool_call → execute → feed back → answer). Keep it short.

> Ask: "Why does the tool description matter more than the prompt for tool selection?" Explain: the LLM reads descriptions to pick tools — poor descriptions mean wrong tools.

> Before implementing, ask: "If the user says 'which lab has the lowest pass rate?', what should happen step by step?" Walk through together.

> When debugging (wrong tool, text instead of tool call), ask: "What do you think went wrong?" Show the actual messages sent to the LLM. Teach the diagnostic process.

> Ask: "What makes a good fallback vs a bad one?" Explain: showing capabilities beats "I don't understand."
