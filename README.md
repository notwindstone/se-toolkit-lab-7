# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

### Optional

1. [Flutter Web Chatbot](./lab/tasks/optional/task-1.md)

## Deploy

This section explains how to deploy the Telegram bot alongside the existing backend using Docker Compose.

### Prerequisites

- Backend is running and healthy (`curl -sf http://localhost:42002/docs` returns 200)
- `.env.docker.secret` contains all required environment variables
- `.env.bot.secret` contains bot-specific credentials (used for local testing)

### Required environment variables

The following variables must be set in `.env.docker.secret`:

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | `8687489478:AAF...` |
| `LMS_API_KEY` | API key for the LMS backend | `my-secret-api-key` |
| `LLM_API_KEY` | API key for the LLM service | `sk-...` |
| `LLM_API_BASE_URL` | LLM API base URL (use `host.docker.internal` for Docker) | `http://host.docker.internal:42005/v1` |
| `LLM_API_MODEL` | LLM model name | `coder-model` |

### Deploy commands

1. **Stop the background bot process** (if running):
   ```bash
   cd ~/se-toolkit-lab-7
   pkill -f "bot.py" 2>/dev/null
   ```

2. **Build and start all services**:
   ```bash
   docker compose --env-file .env.docker.secret up --build -d
   ```

3. **Check service status**:
   ```bash
   docker compose --env-file .env.docker.secret ps
   ```

   You should see `bot` running alongside `backend`, `postgres`, `caddy`.

4. **View bot logs**:
   ```bash
   docker compose --env-file .env.docker.secret logs bot --tail 20
   ```

   Look for "Application started" and no Python tracebacks.

### Verify deployment

**In Telegram:**
1. `/start` — should return welcome message with keyboard buttons
2. `/health` — should show backend status and item count
3. "what labs are available?" — should list all labs (LLM-powered)
4. "which lab has the lowest pass rate?" — should compare all labs (multi-step reasoning)

**On the VM:**
```bash
# Check bot container is running
docker compose --env-file .env.docker.secret ps bot

# Check backend is still healthy
curl -sf http://localhost:42002/docs

# Check git remote matches your repo
git remote get-url origin
```

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Bot container keeps restarting | Check logs: `docker compose logs bot`. Usually missing env var or import error. |
| `/health` fails but worked before | `LMS_API_BASE_URL` must be `http://backend:8000` (not `localhost`). |
| LLM queries fail | `LLM_API_BASE_URL` must use `host.docker.internal` (not `localhost`). |
| "BOT_TOKEN is required" | Add `BOT_TOKEN` to `.env.docker.secret`. |
| Build fails at `uv sync --frozen` | Ensure `bot/uv.lock` exists and is copied in Dockerfile. |

### Stop and restart

```bash
# Stop all services
docker compose --env-file .env.docker.secret down

# Restart bot only
docker compose --env-file .env.docker.secret restart bot

# Rebuild and restart (after code changes)
docker compose --env-file .env.docker.secret up --build -d bot
```
