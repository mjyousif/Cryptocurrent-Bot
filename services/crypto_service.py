"""Business logic for crypto queries.

This module exposes a small API to the controller layer:
- get_crypto_list(query: str) -> list of objects with attributes similar to existing `cryptoClass` (id, name, symbol, price, market_cap, percent_change_* , currency)
- get_coin_ratio(coin1: str, coin2: str) -> Optional[str]

It uses `data.CoinMarketCapClient` and `sorter.valueSorter` internally.
"""

from __future__ import annotations

from typing import List, Optional

import logging
from data.coinmarketcap import CoinMarketCapClient, parse_coin_info
from data.models import CryptoQuote
from sorter import valueSorter

logger = logging.getLogger(__name__)


class FormattedCrypto:
    """Compatibility wrapper matching the old `cryptoClass` interface used by handlers."""

    def __init__(self, quote: CryptoQuote):
        self.id = str(quote.id)
        self.currency = quote.currency
        self.name = quote.name or "N/A"
        self.symbol = quote.symbol or "N/A"
        self.price = self._format_price(quote.price)
        self.market_cap = self._format_price(quote.market_cap)
        self.percent_change_1h = self._format_change(quote.percent_change_1h)
        self.percent_change_24h = self._format_change(quote.percent_change_24h)
        self.percent_change_7d = self._format_change(quote.percent_change_7d)

    @staticmethod
    def _format_price(value: Optional[float]) -> str:
        if value is None or value == 0:
            return "N/A"
        # Replicate previous formatting: commas + decimal precision (2 for >=1 else up to 6)
        if value >= 1.0:
            return f"{value:,.2f}"
        else:
            # 6 decimal places for small values, trimmed
            return f"{value:,.6f}".rstrip("0").rstrip(".")

    @staticmethod
    def _format_change(value: Optional[float]) -> str:
        return "N/A" if value is None else str(value)


def _parse_query(query: str):
    """Parse query into (coin_names:list[str], currency:str, sort_type:str)

    Follows existing behavior: optional trailing sort type, default currency USD.
    """
    accepted_currencies = [
        "AUD",
        "BRL",
        "CAD",
        "CHF",
        "CLP",
        "CNY",
        "CZK",
        "DKK",
        "EUR",
        "GBP",
        "HKD",
        "HUF",
        "IDR",
        "ILS",
        "INR",
        "JPY",
        "KRW",
        "MXN",
        "MYR",
        "NOK",
        "NZD",
        "PHP",
        "PKR",
        "PLN",
        "RUB",
        "SEK",
        "SGD",
        "THB",
        "TRY",
        "TWD",
        "ZAR",
        "USD",
    ]

    query_split = query.split(" ")

    sort_types = ["alpha", "price", "mktcap", "1h", "1d", "7d"]
    if query_split[-1].lower() in sort_types:
        sort_type = query_split[-1]
        # remove the sort token from the working tokens
        del query_split[-1]
    else:
        sort_type = ""

    # Reconstruct a working query string that has the sort token removed
    working_query = " ".join(query_split)

    # default currency: if trailing token is not a currency, append USD
    last_token = query_split[-1] if query_split else ""
    if not last_token.upper() in accepted_currencies:
        working_query += " usd"
    currency = working_query[-3:].upper()

    # coin list parsing (commas, normalize spaces to hyphens)
    q = working_query[:-4].replace(", ", ",").lower()
    coin_list = q.replace(" ", "-").split(",")

    return coin_list, currency, sort_type


def get_crypto_list(query: str) -> List[FormattedCrypto]:
    """Return list of `FormattedCrypto` objects for the provided query.

    If coins cannot be found, returns an empty list.
    """
    logger.info("get_crypto_list called with query=%s", query)
    coin_names, currency, sort_type = _parse_query(query)

    client = CoinMarketCapClient()
    listings = client.get_listings()
    logger.debug("Loaded %d listings from client", len(listings))

    # map coin names/slugs/symbols to ids
    id_map = {}
    for listing in listings:
        id_map.setdefault(listing.get("name", "").lower(), listing["id"])
        id_map.setdefault(listing.get("slug", "").lower(), listing["id"])
        id_map.setdefault(listing.get("symbol", "").lower(), listing["id"])

    id_list = []
    for coin in coin_names:
        if coin in id_map:
            id_list.append(id_map[coin])
        else:
            # skip unknown coins silently (matching prior behavior)
            continue

    if not id_list:
        logger.info("No IDs resolved for query=%s -> returning empty result", query)
        return []

    logger.debug("Resolved ids for query=%s -> %s", query, id_list)
    resp = client.get_quotes(id_list, currency)
    if "data" not in resp:
        logger.warning(
            "No data in quotes response for ids=%s currency=%s", id_list, currency
        )
        return []

    quotes = []
    for coin_id in id_list:
        coin_id_str = str(coin_id)
        if coin_id_str in resp["data"]:
            quote = parse_coin_info(resp["data"][coin_id_str], currency)
            quotes.append(quote)

    # convert to formatted
    formatted = [FormattedCrypto(q) for q in quotes]

    # Apply sorting using existing sorter
    formatted = valueSorter(formatted, sort_type)
    logger.info("Returning %d formatted results for query=%s", len(formatted), query)

    return formatted


def get_coin_ratio(coin1: str, coin2: str) -> Optional[str]:
    """Return coin1 price in terms of coin2 as a formatted string or None if unavailable.

    Accepts coin names/symbols/slugs in the same format as queries.
    """
    logger.info("get_coin_ratio called with %s/%s", coin1, coin2)
    # Use simple classify flow by invoking get_crypto_list for "coin1 coin2" style
    # We'll ask for both coins in USD and compute ratio using the raw float prices
    client = CoinMarketCapClient()

    def _resolve(coin):
        listings = client.get_listings()
        for l in listings:
            if (
                coin == l.get("name", "").lower()
                or coin == l.get("slug", "").lower()
                or coin == l.get("symbol", "").lower()
            ):
                return l["id"]
        return None

    c1 = coin1.replace(" ", "-").lower()
    c2 = coin2.replace(" ", "-").lower()
    id1 = _resolve(c1)
    id2 = _resolve(c2)
    if not id1 or not id2:
        return None

    resp = client.get_quotes([id1, id2], "USD")
    if (
        "data" not in resp
        or str(id1) not in resp["data"]
        or str(id2) not in resp["data"]
    ):
        return None

    p1 = resp["data"][str(id1)]["quote"]["USD"]["price"]
    p2 = resp["data"][str(id2)]["quote"]["USD"]["price"]
    if p1 == 0 or p2 == 0 or p2 is None or p1 is None:
        return None

    ratio = float(p1) / float(p2)
    # Format ratio to up to 8 decimal places like original logic
    ratio_str = f"{ratio:.8f}".rstrip("0").rstrip(".")
    logger.info("Computed ratio %s for %s/%s", ratio_str, coin1, coin2)
    # Comma-format the integer part
    if "." in ratio_str:
        left, right = ratio_str.split(".")
        left = f"{int(left):,}"
        return left + "." + right
    else:
        return f"{int(ratio):,}"
