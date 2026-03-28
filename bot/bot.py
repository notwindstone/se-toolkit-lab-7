"""
LMS Telegram Bot entry point.

Supports --test mode for offline testing without Telegram connection.
In --test mode, plain text messages are routed through the LLM intent router.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_unknown,
)
from handlers.intent_router import handle_natural_language


def process_command(command: str) -> str:
    """Route a command to the appropriate handler."""
    # Parse command and arguments
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # Check if this is a slash command
    if cmd.startswith("/"):
        # Route to slash command handlers
        if cmd == "/start":
            return handle_start()
        elif cmd == "/help":
            return handle_help()
        elif cmd == "/health":
            return handle_health()
        elif cmd == "/labs":
            return handle_labs()
        elif cmd == "/scores":
            return handle_scores(args)
        else:
            return handle_unknown(cmd)
    else:
        # Plain text message - route through LLM intent router
        # The entire message is the input (not just the first word)
        return handle_natural_language(command, debug=True)


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: process a command and print result to stdout"
    )
    args = parser.parse_args()
    
    if args.test:
        # Test mode: process command and print to stdout
        result = process_command(args.test)
        print(result)
        sys.exit(0)
    else:
        # Normal mode: would start Telegram bot
        print("Starting Telegram bot (not implemented in this task)")
        sys.exit(0)


if __name__ == "__main__":
    main()
