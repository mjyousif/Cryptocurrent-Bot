"""Inline query processing logic for building InlineQuery results from query strings.

This centralizes the branching logic (news / multi-coin / ratio / single coin)
so `app.inline_crypto` can delegate to a testable unit.
"""

import logging
import re
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from api import _build_multi_coin_results, _build_single_coin_results
from services.crypto_service import get_coin_ratio, get_crypto_list
from services.feedReader import news

logger = logging.getLogger(__name__)


class InlineQueryProcessor:
    """Process an inline query string and return (results, cache_time).

    - results: list of InlineQueryResult* objects
    - cache_time: int seconds or None (only single-coin uses 300)

    Raises ValueError when a configuration error occurs (e.g. missing API key)
    so callers can convert it to a user-facing InlineQuery result.
    """

    def __init__(self):
        # Define routing rules in order of precedence.
        # The first matching regex decides which handler processes the query.
        self.routes = [
            (re.compile(r"(?i)^news(?:\s+(.+))?$"), self._handle_news),
            (
                re.compile(r"^([a-zA-Z0-9\-\.]+)\s*/\s*([a-zA-Z0-9\-\.]+)$"),
                self._handle_ratio,
            ),
            (
                re.compile(r"^[a-zA-Z0-9\-\.]+(?:,[a-zA-Z0-9\-\.]+)+$"),
                self._handle_multi_coin,
            ),
            (re.compile(r"^(.*)$"), self._handle_single_coin_or_fallback),  # Catch-all
        ]

    def build_results(self, query: str):
        logger.debug("Processing inline query: %s", query)
        query = query.strip()
        if not query:
            return [], None

        for pattern, handler in self.routes:
            match = pattern.match(query)
            if match:
                return handler(match)

        return [], None

    def _handle_news(self, match: re.Match):
        search_term = match.group(1)
        if search_term:
            articles = news(search_term.strip())
        else:
            articles = news()

        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=a.title,
                input_message_content=InputTextMessageContent(a.link),
                description=a.description,
            )
            for a in articles
        ]
        return results, None

    def _handle_ratio(self, match: re.Match):
        coin1, coin2 = match.group(1), match.group(2)
        ratio = get_coin_ratio(coin1, coin2)
        if not ratio:
            return [], None

        description = f"{ratio} {coin1.upper()}/{coin2.upper()}"
        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=f"{coin1} / {coin2}",
                description=description,
                input_message_content=InputTextMessageContent(description),
                thumbnail_url="https://i.postimg.cc/HcxQF59Z/icon-values-1787353167277.jpg",
            )
        ]
        return results, None

    def _handle_multi_coin(self, match: re.Match):
        query = match.string
        crypto_list = get_crypto_list(query)
        if not crypto_list:
            return [], None
        return _build_multi_coin_results(crypto_list), None

    def _handle_single_coin_or_fallback(self, match: re.Match):
        query = match.string
        try:
            crypto_list = get_crypto_list(query)
            if crypto_list:
                results = _build_single_coin_results(crypto_list[0])
                return results, 300
        except ValueError:
            # Ignore configuration errors here and let it fallback to AI
            pass

        return self._handle_ai_fallback(query)

    def _handle_ai_fallback(self, query: str):
        title = "Ask AI ✨"
        description = f"Generate an AI response for: '{query}'"
        results = [
            InlineQueryResultArticle(
                id="ai_fallback",
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    f"Thinking about: {query} 💭..."
                ),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("⏳ Generating...", callback_data="ignore")]]
                ),
            )
        ]
        return results, None
