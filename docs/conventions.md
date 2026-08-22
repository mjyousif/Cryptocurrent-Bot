# Coding Guidelines

1. **Telegram Formatting**: Telegram messages are parsed using `ParseMode.HTML`. When returning text for Telegram, **always use basic HTML tags** (e.g., `<b>`, `<i>`). Do not use standard Markdown formatting (e.g., `**bold**`) as it will cause rendering errors.
2. **Caching Constraints**: Always leverage or respect the existing SQLite/in-memory caching mechanisms for CoinMarketCap data to prevent API exhaustion.
3. **AI Provider Constraints**: `litellm` is used as the unified AI API. Any new AI capabilities should use `litellm.completion` via `data/google_ai.py` rather than importing provider-specific SDKs.
4. **Code Formatting**: Ensure all Python files conform to `black` formatting with an 88-character line length limit.
