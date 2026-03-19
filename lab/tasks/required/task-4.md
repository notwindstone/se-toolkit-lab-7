# Deploy and Document

Deploy the bot on your VM alongside the backend.

## Requirements targeted

- **P3.1** Bot containerized with Dockerfile
- **P3.2** Added as service in `docker-compose.yml`
- **P3.3** Deployed and running on VM
- **P3.4** README documents deployment

## Deliverables

### 1. Bot Dockerfile (`bot/Dockerfile`)

Installs dependencies from `bot/requirements.txt`, runs the bot entry point.

### 2. Bot service in `docker-compose.yml`

- Connects to backend via Docker network (service name, not `localhost`)
- Reads `BOT_TOKEN` and LLM credentials from environment
- Restarts unless stopped

### 3. Deployment verification

Bot container runs alongside backend on VM. Both healthy.

### 4. README deploy section

How to deploy: env vars, docker compose commands, verification.

## Acceptance criteria

- [ ] Repo deployed at `~/se-toolkit-lab-7` on VM.
- [ ] `git remote get-url origin` matches student's GitHub repo.
- [ ] `docker-compose.yml` includes a bot service.
- [ ] Bot container running (`docker ps` shows it).
- [ ] Backend still healthy (`curl -sf http://localhost:42002/docs` returns 200).
- [ ] README has a section with "deploy" in heading.
- [ ] Bot responds in Telegram (TA-verified).

## Agent instructions

Follow these to maximize learning. Do not skip.

**Engage before explaining.** Ask first, let the student think, then fill gaps.

> Ask: "Why do we use multi-stage Docker builds?" Explain: build deps stay in builder stage, final image is smaller and more secure.

> Ask: "The bot needs to reach the backend. Can it use `localhost`?" Explain Docker networking: Compose creates a shared network, services use service names.

> When debugging connectivity, ask: "How would you diagnose this?" Show: `docker compose logs bot`, `docker exec`, check env vars. Teach the process.

> Ask: "What would a new developer need to know to deploy this?" Use their answer as the README outline.
