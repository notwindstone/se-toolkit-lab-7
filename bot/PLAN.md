# LMS Telegram Bot Development Plan

## Overview

This document outlines the development plan for building a Telegram bot that integrates with the LMS (Learning Management System) backend. The bot will provide students with access to their labs, scores, and other course-related information through a conversational interface.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry Point (`bot.py`)**: Handles Telegram bot initialization and `--test` mode for offline testing. Routes incoming messages to appropriate handlers.

2. **Handlers (`handlers/`)**: Plain Python functions that process commands and return text responses. They are completely independent of Telegram, making them testable without a Telegram connection.

3. **Services (`services/`)**: External service clients including the LMS API client and LLM client. These handle HTTP requests, authentication, and response parsing.

4. **Configuration (`config.py`)**: Environment variable loading using `pydantic-settings` for type-safe configuration management.

## Task Breakdown

### Task 1: Plan and Scaffold

Create the project skeleton with testable handler architecture. Implement `--test` mode that allows testing commands without Telegram. Add placeholder handlers for `/start`, `/help`, `/health`, `/labs`, and `/scores`.

### Task 2: Backend Integration

Implement the LMS API client with Bearer token authentication. Replace placeholder handlers with real API calls to fetch labs and scores. Handle API errors gracefully with informative messages.

### Task 3: LLM Intent Routing

Add an LLM client that uses tool descriptions to route natural language queries to the appropriate handlers. Users can ask "what labs are available?" instead of typing `/labs`. The LLM decides which tool to call based on the descriptions.

### Task 4: Docker Deployment

Containerize the bot for deployment. Configure Docker networking so the bot container can communicate with the backend using service names instead of `localhost`. Set up environment variables for production.

## Testing Strategy

- **Unit tests**: Test handlers directly with various inputs
- **Test mode**: Use `--test` flag for manual command testing
- **Integration tests**: Verify API client handles real responses
- **Telegram testing**: Deploy and test in real Telegram environment

## Dependencies

- `aiogram`: Async Telegram bot framework
- `httpx`: Async HTTP client for API calls
- `pydantic-settings`: Type-safe configuration management
