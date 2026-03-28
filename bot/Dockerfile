# Bot Dockerfile
# Uses uv for dependency management (not pip/requirements.txt)
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Copy the entire project for workspace support
COPY pyproject.toml uv.lock ./
COPY backend/ ./backend/
COPY bot/ ./bot/

# Install dependencies using uv (workspace mode)
RUN uv sync --frozen --no-dev

# Set working directory to app so imports work correctly
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Run the bot
CMD ["uv", "run", "bot/bot.py"]
