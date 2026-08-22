# Tech Stack & Environment

## Tech Stack & Dependencies
- **Language**: Python 3.10+
- **Dependency Manager**: `uv` (use `uv sync` to install/update dependencies)
- **Bot Framework**: `python-telegram-bot` (v20+)
- **LLM Interface**: `litellm` (defaulting to Google Gemini models)
- **Data Source**: CoinMarketCap Pro API, feedparser (for RSS news)
- **Formatter**: `black`

## Environment & Execution
- Use `uv run <command>` to execute commands in the virtual environment.
- Run the bot locally: `uv run app.py`
- Format code: `uv run black .`
- **Environment Variables** (see `env.example`):
  - `TELEGRAM_BOT_TOKEN`
  - `COINMARKETCAP_API_KEY`
  - `GEMINI_API_KEY` (Required for `litellm` AI fallbacks and summaries)
