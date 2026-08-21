# CryptoCurrent Bot - Feature Overview

This document provides an exhaustive list of the current features implemented in the CryptoCurrent telegram bot.

## 1. Inline Cryptocurrency Information
The bot operates inline, meaning it can be called from any chat by typing `@CryptoCurrent_bot` followed by a query. It responds with an inline panel showing current market data.

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
Users can fetch the latest cryptocurrency news articles directly inline. It searches across CoinDesk, CoinTelegraph, and TheMerkle.
- **Format (Latest News):** `@CryptoCurrent_bot news`
- **Format (News by tag/topic):** `@CryptoCurrent_bot news <search term>`
- **Example:** `@CryptoCurrent_bot news bitcoin`

## 4. Supported Output Currencies
By default, the bot outputs data in USD, but it supports specifying an output fiat currency from a wide list of options, including:
`AUD, BRL, CAD, CHF, CLP, CNY, CZK, DKK, EUR, GBP, HKD, HUF, IDR, ILS, INR, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PKR, PLN, RUB, SEK, SGD, THB, TRY, TWD, ZAR, USD`.

## 5. Data Providers and Integrations
- **CoinMarketCap Pro API:** The bot fetches its primary cryptocurrency data from the CoinMarketCap Pro API.
- **Google AI Summary:** For single-coin queries, the bot integrates with Google AI to provide a "bombastic and truthful" 2-3 sentence market summary of the coin. This is triggered via an inline callback button (`AI summary`) attached to the inline query result.
