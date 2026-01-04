# Docker Setup for CryptoCurrent Bot

This guide explains how to run the CryptoCurrent bot using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)

## Quick Start

### Using Docker Compose (Recommended)

1. **Create a `.env` file** in the project root with your credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here
   WEBHOOK_URL=  # Optional: leave empty for long-polling
   ```

2. **Build and run the container**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container**:
   ```bash
   docker-compose down
   ```

### Using Docker directly

1. **Build the image**:
   ```bash
   docker build -t cryptocurrent-bot .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name cryptocurrent-bot \
     --restart unless-stopped \
     -e TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here \
     -e COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here \
     -v $(pwd)/coinmarketcap_cache.sqlite:/app/coinmarketcap_cache.sqlite \
     cryptocurrent-bot
   ```

3. **View logs**:
   ```bash
   docker logs -f cryptocurrent-bot
   ```

4. **Stop the container**:
   ```bash
   docker stop cryptocurrent-bot
   docker rm cryptocurrent-bot
   ```

## Environment Variables

- `TELEGRAM_BOT_TOKEN` (required): Your Telegram bot token from @BotFather
- `COINMARKETCAP_API_KEY` (required): Your CoinMarketCap Pro API key
- `WEBHOOK_URL` (optional): Webhook URL for production deployments. Leave empty to use long-polling.

## Notes

- The SQLite cache file is persisted using a volume mount to preserve data between container restarts
- The container runs as a non-root user for security
- The container will automatically restart unless stopped manually

