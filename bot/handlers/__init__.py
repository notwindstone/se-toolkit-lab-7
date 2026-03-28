"""
Command handlers for the LMS Bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram - this makes them testable.
"""


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores - View your scores"
    )


def handle_health() -> str:
    """Handle /health command."""
    return "Backend status: OK (placeholder)"


def handle_labs() -> str:
    """Handle /labs command."""
    return "Available labs: (placeholder)"


def handle_scores(args: str = "") -> str:
    """Handle /scores command."""
    if args:
        return f"Scores for {args}: (placeholder)"
    return "Your scores: (placeholder)"


def handle_unknown(command: str) -> str:
    """Handle unknown commands."""
    return f"Unknown command: {command}. Use /help to see available commands."
