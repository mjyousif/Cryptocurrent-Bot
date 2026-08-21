# CryptoCurrent Bot 📈

A Telegram inline bot that provides real-time cryptocurrency information right in your chat.

## Features

* **Single Coin Lookup**: Get current information about any cryptocurrency by its name or symbol.
* **Multi-Coin Comparison**: Fetch data for several coins in a single message for quick comparison.
* **Currency Conversion**: Request crypto prices in over 30 different fiat currencies (USD, EUR, GBP, JPY, etc.).
* **News Feed**: Get the latest cryptocurrency news articles inline.
* **Smart Caching**: Efficiently caches CoinMarketCap data using SQLite to minimize API requests and improve response times.

## Prerequisites

* Python 3.10+ or Docker
* A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
* A CoinMarketCap API Key (from [CoinMarketCap API](https://coinmarketcap.com/api/))

## Setup & Installation

You can run the bot natively using Python or via Docker.

### Option 1: Native Python

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   Copy the example environment file and fill in your keys:
   ```bash
   cp env.example .env
   ```
   Add your `TELEGRAM_BOT_TOKEN` and `COINMARKETCAP_API_KEY`.

3. **Run the bot**:
   ```bash
   python app.py
   ```

### Option 2: Docker (Recommended)

1. **Configure environment variables**:
   Create a `.env` file in the project root with your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here
   ```

2. **Build and run the container**:
   ```bash
   docker-compose up -d
   ```

3. **View logs or stop the container**:
   ```bash
   docker-compose logs -f
   docker-compose down
   ```

## Usage

To use the bot, simply type `@CryptoCurrent_bot` (or your own bot's username) in any Telegram chat, followed by your query.

### Single Coin Information
```text
@CryptoCurrent_bot <crypto_name_or_symbol> [fiat_currency]
```
* **Example**: `@CryptoCurrent_bot bitcoin` or `@CryptoCurrent_bot btc eur`
* *Note: Case does not matter. Names with spaces like "Bitcoin Cash" are supported.*

### Multi-Coin Comparison
```text
@CryptoCurrent_bot <coin1>,<coin2>,<coin3> [fiat_currency]
```
* **Example**: `@CryptoCurrent_bot btc,eth,ltc gbp`
* *Note: Separate coins with a comma. You can enter as many as you want.*

### Supported Fiat Currencies
The bot supports the following fiat output currencies:
`AUD`, `BRL`, `CAD`, `CHF`, `CLP`, `CNY`, `CZK`, `DKK`, `EUR`, `GBP`, `HKD`, `HUF`, `IDR`, `ILS`, `INR`, `JPY`, `KRW`, `MXN`, `MYR`, `NOK`, `NZD`, `PHP`, `PKR`, `PLN`, `RUB`, `SEK`, `SGD`, `THB`, `TRY`, `TWD`, `ZAR`, `USD`
