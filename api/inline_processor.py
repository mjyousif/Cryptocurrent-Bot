"""Inline query processing logic for building InlineQuery results from query strings.

This centralizes the branching logic (news / multi-coin / ratio / single coin)
so `app.inline_crypto` can delegate to a testable unit.
"""

from uuid import uuid4
import logging
from telegram import (
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)

from api import _build_multi_coin_results, _build_single_coin_results
from services.crypto_service import get_crypto_list, get_coin_ratio
from feedReader import news

logger = logging.getLogger(__name__)


class InlineQueryProcessor:
    """Process an inline query string and return (results, cache_time).

    - results: list of InlineQueryResult* objects
    - cache_time: int seconds or None (only single-coin uses 300)

    Raises ValueError when a configuration error occurs (e.g. missing API key)
    so callers can convert it to a user-facing InlineQuery result.
    """

    def build_results(self, query: str):
        logger.debug("Processing inline query: %s", query)
        if not query:
            return [], None

        news_query = query.split(" ")
        if news_query[0].lower() == "news":
            # Merge the rest of the tokens into a single search term like the old logic
            if len(news_query) == 1:
                articles = news()
            else:
                articles = news(" ".join(news_query[1:]))
            results = []
            for a in articles:
                results.append(
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=a.title,
                        input_message_content=InputTextMessageContent(a.link),
                        description=a.description,
                    )
                )
            return results, None

        # Multi-coin queries like "btc,eth"
        if "," in query:
            try:
                crypto_list = get_crypto_list(query)
            except ValueError:
                # propagate configuration errors to caller
                raise
            if not crypto_list:
                return [], None
            results = _build_multi_coin_results(crypto_list)
            return results, None

        # Ratio queries like "btc/eth"
        if "/" in query:
            parts = [p.strip() for p in query.split("/") if p.strip()]
            if len(parts) != 2:
                return [], None
            try:
                ratio = get_coin_ratio(parts[0], parts[1])
            except ValueError:
                raise
            if not ratio:
                return [], None
            title = f"{parts[0]} / {parts[1]}"
            description = f"{ratio} {parts[0].upper()}/{parts[1].upper()}"
            results = [
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=title,
                    description=description,
                    input_message_content=InputTextMessageContent(f"{description}"),
                    thumbnail_url="https://i.imgur.com/My7IG7r.png",
                )
            ]
            return results, None

        # Single coin fallback
        try:
            crypto_list = get_crypto_list(query)
        except ValueError:
            raise
        if not crypto_list:
            return [], None
        coin = crypto_list[0]
        results = _build_single_coin_results(coin)
        # Original behavior used cache_time=300 for single coin responses
        return results, 300
