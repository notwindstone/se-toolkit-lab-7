"""
Command handlers for the LMS Bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram - this makes them testable.
"""

from services.api_client import lms_client, LMSAPIError

# Inline keyboard button definitions for Telegram
# These are shown after /start to help users discover actions
KEYBOARD_BUTTONS = [
    ["📊 Check backend health", "/health"],
    ["📚 List available labs", "/labs"],
    ["📈 View scores for lab-04", "/scores lab-04"],
    ["❓ Show help", "/help"],
]


def get_keyboard_markup() -> str:
    """
    Return keyboard button configuration.
    In Telegram, these would be inline keyboard buttons.
    For --test mode, we show them as text suggestions.
    """
    lines = ["\nQuick actions:"]
    for label, command in KEYBOARD_BUTTONS:
        lines.append(f"  {label} → `{command}`")
    return "\n".join(lines)


def handle_start() -> str:
    """Handle /start command."""
    return (
        "Welcome to the LMS Bot! 👋\n\n"
        "I can help you check backend status, list available labs, and view your scores.\n"
        "You can use slash commands OR just ask me questions in plain English!\n\n"
        "Try asking:\n"
        "  • \"what labs are available?\"\n"
        "  • \"show me scores for lab 4\"\n"
        "  • \"which lab has the lowest pass rate?\"\n"
        "  • \"who are the top 5 students in lab-04?\""
        f"{get_keyboard_markup()}"
    )


def handle_help() -> str:
    """Handle /help command."""
    return (
        "Available commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status and item count\n"
        "/labs - List all available labs\n"
        "/scores <lab> - View pass rates for a specific lab (e.g., /scores lab-04)"
    )


def handle_health() -> str:
    """Handle /health command."""
    try:
        count = lms_client.get_item_count()
        return f"Backend is healthy. {count} items available."
    except LMSAPIError as e:
        return f"Backend error: {str(e)}"


def handle_labs() -> str:
    """Handle /labs command."""
    try:
        items = lms_client.get_items()
        # Filter only labs (type == "lab")
        labs = [item for item in items if item.get("type") == "lab"]
        
        if not labs:
            return "No labs found in the backend."
        
        lines = ["Available labs:"]
        for lab in labs:
            title = lab.get("title", "Unknown")
            lines.append(f"- {title}")
        
        return "\n".join(lines)
    except LMSAPIError as e:
        return f"Backend error: {str(e)}"


def handle_scores(args: str = "") -> str:
    """Handle /scores command."""
    if not args:
        return "Usage: /scores <lab> (e.g., /scores lab-04)"
    
    try:
        pass_rates = lms_client.get_pass_rates(args)
        
        if not pass_rates:
            return f"No pass rate data found for '{args}'."
        
        # Extract lab number from lab ID for display
        lab_display = args.replace("-", " ").title()
        lines = [f"Pass rates for {lab_display}:"]
        
        for rate in pass_rates:
            task = rate.get("task", "Unknown task")
            avg_score = rate.get("avg_score", 0)
            attempts = rate.get("attempts", 0)
            lines.append(f"- {task}: {avg_score:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
    except LMSAPIError as e:
        return f"Backend error: {str(e)}"


def handle_unknown(command: str) -> str:
    """Handle unknown commands."""
    return f"Unknown command: {command}. Use /help to see available commands."
