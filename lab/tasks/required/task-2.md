# Backend Integration

Connect the bot to your LMS backend with real data commands.

## Requirements targeted

- **P0.3** `/start` — welcome message
- **P0.4** `/help` — lists all available commands
- **P0.5** `/health` — calls backend, reports up/down status
- **P0.6** `/labs` — lists available labs
- **P0.7** `/scores <lab>` — per-task pass rates
- **P0.8** Error handling — friendly message when backend is down

## What you will build

5 slash commands hitting the real backend, verifiable via `--test`:

```terminal
$ python bot/bot.py --test "/health"
Backend is healthy. 42 items available.

$ python bot/bot.py --test "/labs"
Available labs:
- Lab 01 — Products, Architecture & Roles
- Lab 02 — Run, Fix, and Deploy
...

$ python bot/bot.py --test "/scores lab-04"
Pass rates for Lab 04:
- Repository Setup: 92.1% (187 attempts)
- Back-end Testing: 71.4% (156 attempts)
```

## Backend endpoints

All on `localhost:42002`, require `Authorization: Bearer YOUR_LMS_API_KEY`:

| Endpoint | Returns |
|----------|---------|
| `GET /items/` | Labs and tasks |
| `GET /learners/` | Enrolled students |
| `GET /analytics/scores?lab=lab-01` | Score distribution (4 buckets) |
| `GET /analytics/pass-rates?lab=lab-01` | Per-task averages |
| `GET /analytics/timeline?lab=lab-01` | Submissions per day |
| `GET /analytics/groups?lab=lab-01` | Per-group performance |
| `GET /analytics/top-learners?lab=lab-01&limit=5` | Top N learners |
| `GET /analytics/completion-rate?lab=lab-01` | Completion percentage |
| `POST /pipeline/sync` | Trigger ETL sync |

> [!TIP]
> Explore these in Swagger UI at `http://localhost:42002/docs` first.

## Required commands

| Command | Endpoint | What it does |
|---------|----------|-------------|
| `/start` | — | Welcome message |
| `/help` | — | Lists all commands |
| `/health` | `GET /items/` | Reports healthy/unhealthy |
| `/labs` | `GET /items/` | Lists labs (filter by type) |
| `/scores <lab>` | `GET /analytics/pass-rates?lab=` | Per-task scores |

When the backend is down, show a friendly message — not a traceback.

## Acceptance criteria

- [ ] `--test "/start"` returns text containing "welcome" or bot name.
- [ ] `--test "/help"` lists at least 4 `/command` entries.
- [ ] `--test "/health"` returns a status indicator.
- [ ] `--test "/labs"` lists at least 2 labs.
- [ ] `--test "/scores lab-04"` shows task names and scores.
- [ ] With backend stopped, `--test "/health"` returns friendly message, no `Traceback`.
- [ ] Git workflow followed.

## Agent instructions

Follow these to maximize learning. Do not skip.

**Engage before explaining.** Ask first, let the student think, then fill gaps.

**Build incrementally.** One command at a time. Test with `--test` after each. Don't implement all 5 at once.

> Before each command, ask: "What HTTP call does this need? What could go wrong?" Fill in: status codes, auth, network errors.

> Show the actual API response before formatting. Ask: "How would you present this to a user?"

> For error handling, ask: "What should the user see when the backend is down?" Explain specific exception types vs bare `except:`.

> After each command, run `--test` and ask: "Does this make sense? Edge cases?"
