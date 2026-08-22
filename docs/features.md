# End User Features & Usage

This document details all end-user features of the CryptoCurrent-Bot and how to use them within Telegram.

## 1. Inline Cryptocurrency Information
The bot operates inline, meaning it can be called from any chat without needing to message the bot directly. Type `@CryptoCurrent_bot` followed by your query.

### Single Coin Lookup
Retrieve the price, market capitalization, and percentage changes for a single cryptocurrency.
- **Format:** `@CryptoCurrent_bot <coin name or symbol> [currency symbol]`
- **Example:** `@CryptoCurrent_bot bitcoin` or `@CryptoCurrent_bot btc EUR`

### Multi-Coin Comparison
Retrieve information about several coins in one message by separating the coin names/symbols with commas.
- **Format:** `@CryptoCurrent_bot <coin-1>,<coin-2>,...<coin-n> [currency symbol] [sort_type]`
- **Example:** `@CryptoCurrent_bot btc,eth,doge`

### Result Sorting
For multi-coin queries, users can append a sort type to the end of their query to order the output.
- **Supported Sort Types:** `alpha`, `price`, `mktcap`, `1h`, `1d`, `7d`
- **Example:** `@CryptoCurrent_bot btc,eth,ada,xmr mktcap`

## 2. Coin Ratios (Trading Pairs)
Users can calculate the price ratio between two different cryptocurrencies.
- **Format:** `@CryptoCurrent_bot <coin1>/<coin2>`
- **Example:** `@CryptoCurrent_bot btc/eth`

## 3. Cryptocurrency News
Users can fetch the latest cryptocurrency news articles directly inline. The bot searches across CoinDesk, CoinTelegraph, and TheMerkle.
- **Format (Latest News):** `@CryptoCurrent_bot news`
- **Format (News by tag/topic):** `@CryptoCurrent_bot news <search term>`
- **Example:** `@CryptoCurrent_bot news bitcoin`

## 4. AI Features

### Natural Language Fallback
If the query doesn't match standard commands (like single/multi coins, news, or ratios), it falls back to an AI agent that can understand natural language. It will extract the mentioned coins and any general news keywords (like 'SEC', 'FED'), look up live market data and recent news articles, and generate a context-aware response.
- **Format:** `@CryptoCurrent_bot <natural language question>`
- **Example:** `@CryptoCurrent_bot what did the SEC say about Ethereum today?`

### AI Summaries
For single-coin queries, users can click the inline callback button labeled **`AI summary`** attached to the result. This triggers the AI to provide a fun and truthful 2-3 sentence market summary of the coin based on live data.

## 5. Supported Output Currencies
By default, the bot outputs data in USD, but it supports specifying an output fiat currency from a wide list of options, including:
`AUD, BRL, CAD, CHF, CLP, CNY, CZK, DKK, EUR, GBP, HKD, HUF, IDR, ILS, INR, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PKR, PLN, RUB, SEK, SGD, THB, TRY, TWD, ZAR, USD`.
