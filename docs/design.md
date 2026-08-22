# CryptoCurrent-Bot Design & Architecture

## Core Workflow
CryptoCurrent-Bot is a Telegram inline bot. Users type `@CryptoCurrent_bot <query>` in any chat. The bot fetches data via CoinMarketCap, caches it locally using SQLite to avoid rate limits, and returns an interactive inline result panel.

## AI Fallback
Natural language queries fall back to a `litellm` powered processing chain that extracts intents, pulls live market data, and synthesizes answers.

## Project Structure
- `app.py`: Main entry point containing Telegram handlers (e.g., `inline_crypto`, `button`, `handle_chosen_inline_result`).
- `api/`: API boundary for constructing inline Telegram query results (`InlineQueryResultArticle`, etc.).
- `services/`: Core business logic including:
  - `crypto_service.py`: Managing CMC quotes and ratios.
  - `sorter.py`: Multi-coin sorting mechanisms.
  - `feedReader.py`: Crypto news aggregation.
  - `ai_fallback.py`: NLP query routing and fallback logic.
- `data/`: Core data access layer.
  - `coinmarketcap.py`: Wrapper for CoinMarketCap Pro API.
  - `google_ai.py`: LiteLLM wrapper for generating content.
- `tests/`: Automated unit and integration tests.
