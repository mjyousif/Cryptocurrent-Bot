"""CoinMarketCap client for fetching listings and quotes.

This module provides a light wrapper around the public CoinMarketCap pro endpoints
used in the project. It returns raw JSON or typed dataclass objects (CryptoQuote).
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List

import requests

from .models import CryptoQuote

logger = logging.getLogger(__name__)


class CoinMarketCapClient:
    """Lightweight client for CoinMarketCap Pro API.

    Usage:
        client = CoinMarketCapClient()
        listings = client.get_listings()
        quotes = client.get_quotes([1,2,3], "USD")
    """

    BASE = "https://pro-api.coinmarketcap.com/v1/cryptocurrency"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("COINMARKETCAP_API_KEY")
        if not self.api_key:
            raise ValueError(
                "COINMARKETCAP_API_KEY environment variable is not set. "
                "Please set it in your .env file or as an environment variable."
            )
        self._sess = requests.Session()
        self._sess.headers.update({"X-CMC_PRO_API_KEY": self.api_key})
        # Simple in-memory cache for listings (id -> data) with TTL
        self._listings_cache: dict = {"data": None, "ts": 0}
        self._listings_ttl: int = 60 * 60  # 1 hour

        logger.debug(
            "CoinMarketCapClient initialized (listings_ttl=%s)",
            self._listings_ttl,
        )

    def get_listings(self) -> List[Dict[str, Any]]:
        """Return the data list from /v1/cryptocurrency/map.

        Cached for `self._listings_ttl` seconds.
        """
        now = time.time()
        if (
            self._listings_cache["data"] is not None
            and now - self._listings_cache["ts"] < self._listings_ttl
        ):
            logger.debug(
                "Listings cache hit (age=%s seconds)",
                int(now - self._listings_cache["ts"]),
            )
            return self._listings_cache["data"]

        url = f"{self.BASE}/map"
        logger.info("Fetching listings from CoinMarketCap: %s", url)
        try:
            r = self._sess.get(url)
            if r.status_code != 200:
                logger.error(
                    "CoinMarketCap listings request failed: status=%s body=%s",
                    r.status_code,
                    r.text,
                )
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(
                "Failed to fetch listings (HTTPError): %s response=%s",
                e,
                getattr(e.response, "text", None),
            )
            raise
        except Exception as e:
            logger.exception("Failed to fetch listings: %s", e)
            raise
        data = r.json().get("data", [])
        self._listings_cache["data"] = data
        self._listings_cache["ts"] = now
        logger.debug("Fetched %d listings", len(data))
        return data

    def get_quotes(self, ids: List[int] | str, convert: str = "USD") -> Dict[str, Any]:
        """Return the full response JSON for /v1/cryptocurrency/quotes/latest.

        `ids` may be a list of integers or a comma-separated string of ids.
        """
        if isinstance(ids, list):
            ids = ",".join(str(x) for x in ids)
        params = {"id": ids, "convert": convert}
        url = f"{self.BASE}/quotes/latest"
        logger.info("Fetching quotes for ids=%s convert=%s", ids, convert)
        try:
            r = self._sess.get(url, params=params)
            if r.status_code != 200:
                logger.error(
                    "CoinMarketCap quotes request failed: status=%s body=%s",
                    r.status_code,
                    r.text,
                )
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(
                "Failed to fetch quotes for ids=%s (HTTPError): %s response=%s",
                ids,
                e,
                getattr(e.response, "text", None),
            )
            raise
        except Exception as e:
            logger.exception("Failed to fetch quotes for ids=%s: %s", ids, e)
            raise
        return r.json()


def parse_coin_info(coin_info: Dict[str, Any], currency: str) -> CryptoQuote:
    """Convert a coinInfo item from CMC response into `CryptoQuote` dataclass.

    Note: returns `None` for fields that are missing (CMC may return nulls).
    """
    quote = coin_info.get("quote", {}).get(currency, {})

    def get_val(k):
        v = quote.get(k)
        return None if v is None else float(v)

    return CryptoQuote(
        id=int(coin_info["id"]),
        name=coin_info.get("name") or "",
        symbol=coin_info.get("symbol") or "",
        price=get_val("price"),
        market_cap=get_val("market_cap"),
        percent_change_1h=get_val("percent_change_1h"),
        percent_change_24h=get_val("percent_change_24h"),
        percent_change_7d=get_val("percent_change_7d"),
        currency=currency,
    )
