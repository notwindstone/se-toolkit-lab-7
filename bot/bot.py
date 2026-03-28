"""
LMS Telegram Bot entry point.

Supports --test mode for offline testing without Telegram connection.
In --test mode, plain text messages are routed through the LLM intent router.
In normal mode, runs as a Telegram bot using aiogram.
"""

import argparse
import asyncio
import logging
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        return handle_natural_language(command, debug=False)


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
        # Normal mode: start Telegram bot
        logger.info("Starting Telegram bot...")
        run_telegram_bot()


def run_telegram_bot():
    """Run the Telegram bot using aiogram."""
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command, CommandStart
    from config import settings

    # Initialize bot and dispatcher
    if not settings.bot_token:
        logger.error("BOT_TOKEN is not set")
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        """Handle /start command."""
        await message.answer(handle_start())

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        """Handle /help command."""
        await message.answer(handle_help())

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        """Handle /health command."""
        await message.answer(handle_health())

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        """Handle /labs command."""
        await message.answer(handle_labs())

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        """Handle /scores command."""
        args = message.text.split(maxsplit=1)
        arg = args[1] if len(args) > 1 else ""
        await message.answer(handle_scores(arg))

    @dp.message()
    async def handle_message(message: types.Message):
        """Handle all other messages (plain text)."""
        if message.text:
            # Send typing action
            await bot.send_chat_action(message.chat.id, "typing")
            
            # Process through LLM intent router
            response = process_command(message.text)
            await message.answer(response)

    # Start polling
    logger.info("Bot is running...")
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
