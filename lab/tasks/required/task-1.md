# Plan and Scaffold

Use your coding agent to create a development plan and project skeleton for the Telegram bot.

## Requirements targeted

- **P0.1** Testable handler architecture — handlers work without Telegram
- **P0.2** CLI test mode: `python bot/bot.py --test "/command"` prints response to stdout

## What you will build

A `bot/` directory with entry point, handler layer, configuration, dependencies, and `--test` mode.

```
se-toolkit-lab-7/
├── bot/                    ← NEW
│   ├── bot.py              ← entry point (Telegram + --test mode)
│   ├── handlers/           ← command handlers (no Telegram dependency)
│   ├── services/           ← API client, LLM client
│   ├── config.py           ← env var loading
│   ├── requirements.txt    ← bot dependencies
│   └── PLAN.md             ← development plan
├── backend/                ← existing
├── frontend/               ← existing
└── docker-compose.yml      ← existing
```

## Test mode

The autochecker verifies the bot via `--test` — no Telegram needed:

```terminal
python bot/bot.py --test "/start"
python bot/bot.py --test "/help"
python bot/bot.py --test "/health"
python bot/bot.py --test "/scores lab-04"
python bot/bot.py --test "what labs are available"    # Task 3
```

- Prints response to **stdout**, exits with code **0**
- Reads config from `.env.agent.secret` (`LMS_API_URL`, `LMS_API_KEY`, `LLM_API_KEY`)
- Does **not** connect to Telegram

## Deliverables

### 1. Development plan (`bot/PLAN.md`)

Describe the approach for all tasks (scaffold, backend integration, intent routing, deployment). At least 100 words.

### 2. Bot entry point (`bot/bot.py`)

Must support `--test` mode. Handlers can return placeholder text for now.

### 3. Handler directory (`bot/handlers/`)

Handler modules separated from Telegram transport. `--test` calls them directly.

### 4. Dependencies (`bot/requirements.txt`)

Must install without errors.

### 5. Environment example (`.env.agent.example`)

Add `BOT_TOKEN`, `LMS_API_URL`, `LMS_API_KEY` with placeholder values. Students copy to `.env.agent.secret` and fill in real values.

## Acceptance criteria

- [ ] `bot/PLAN.md` exists with at least 100 words.
- [ ] `.env.agent.example` contains `BOT_TOKEN`, `LMS_API_URL`, `LMS_API_KEY`.
- [ ] `bot/requirements.txt` exists and installs without errors.
- [ ] `bot/handlers/` directory exists with at least one module.
- [ ] `python bot/bot.py --test "/start"` exits 0 with non-empty output.
- [ ] Repo is cloned at `~/se-toolkit-lab-7` on the VM.
- [ ] Git workflow followed (issue, branch, PR, review, merge).

## Agent instructions

Follow these to maximize learning. Do not skip.

**Engage before explaining.** Ask a brief question, let the student think, then fill gaps concisely. If they already understand, move on.

**Before scaffolding:**

> Ask: "Do you know what 'testable handler architecture' means?" The student likely doesn't — explain: a handler is a function that takes input and returns a response. If it depends on Telegram, you can't test it without a running bot. As a plain function, you can call it from `--test`, from tests, or from Telegram — same logic, different entry points.

> Ask: "What should `--test` mode do?" Fill in gaps, then walk through what happens when `python bot/bot.py --test "/start"` runs.

**While planning:**

> Ask the student about their preferences: Telegram library, file organization, naming. The plan should reflect their decisions. Explain each file's responsibility in one sentence.

**While scaffolding:**

> Explain each file as you create it. After scaffolding, ask: "Can you trace the code path when `--test "/start"` runs?"

**After verifying:**

> Ask: "If you wanted to add `/foo`, what would you change?" Make sure they can answer.
