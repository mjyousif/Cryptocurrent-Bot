"""API view helpers for building Telegram InlineQuery results.

This package centralizes presentation helpers (moved from the top-level `api.py`).
"""

import logging
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)

logger = logging.getLogger(__name__)


def _build_multi_coin_results(cryptoList):
    """Build InlineQuery results for a multi-coin query."""
    logger.debug(
        "Building multi-coin results for %d coin(s): %s",
        len(cryptoList),
        [c.symbol for c in cryptoList],
    )
    nameList = []
    symbolValueList = []
    symbolCapList = []
    symbolHourList = []
    symbolDayList = []
    symbolWeekList = []

    valueList = ["Values:"]
    capList = ["Market Caps:"]
    hourList = ["1 Hour Changes:"]
    dayList = ["1 Day Changes:"]
    weekList = ["7 Day Changes:"]

    for coin in cryptoList:
        nameList.append(f"{coin.name} ({coin.symbol})")
        symbolValueList.append(
            f"{coin.symbol}: {coin.price} {coin.currency if coin.price != 'N/A' else ''}"
        )
        symbolCapList.append(
            f"{coin.symbol}: {coin.market_cap} {coin.currency if coin.market_cap != 'N/A' else ''}"
        )
        symbolHourList.append(f"{coin.symbol}: {coin.percent_change_1h}%")
        symbolDayList.append(f"{coin.symbol}: {coin.percent_change_24h}%")
        symbolWeekList.append(f"{coin.symbol}: {coin.percent_change_7d}%")

        valueList.append(
            f"{coin.name} ({coin.symbol}): {coin.price} {coin.currency if coin.price != 'N/A' else ''}"
        )
        capList.append(
            f"{coin.name} ({coin.symbol}): {coin.market_cap} {coin.currency if coin.market_cap != 'N/A' else ''}"
        )
        hourList.append(f"{coin.name} ({coin.symbol}): {coin.percent_change_1h}%")
        dayList.append(f"{coin.name} ({coin.symbol}): {coin.percent_change_24h}%")
        weekList.append(f"{coin.name} ({coin.symbol}): {coin.percent_change_7d}%")

    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title=", ".join(nameList),
            input_message_content=InputTextMessageContent("\n".join(nameList)),
            thumbnail_url="https://i.postimg.cc/w3r9ybwq/icon-multi-coin.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title=f"{cryptoList[0].currency} Values",
            description="|".join(symbolValueList),
            input_message_content=InputTextMessageContent("\n".join(valueList)),
            thumbnail_url="https://i.postimg.cc/JGBMbc2f/icon-values.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title=f"{cryptoList[0].currency} Market Capitalizations",
            description="|".join(symbolCapList),
            input_message_content=InputTextMessageContent("\n".join(capList)),
            thumbnail_url="https://i.postimg.cc/YjPtGydB/icon-market-cap.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="One Hour Changes",
            description="|".join(symbolHourList),
            input_message_content=InputTextMessageContent("\n".join(hourList)),
            thumbnail_url="https://i.postimg.cc/Cd2wB6cg/icon-1h-change.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="One Day Changes",
            description="|".join(symbolDayList),
            input_message_content=InputTextMessageContent("\n".join(dayList)),
            thumbnail_url="https://i.postimg.cc/RqYv6bXk/icon-1d-change.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Seven Day Changes",
            description="|".join(symbolWeekList),
            input_message_content=InputTextMessageContent("\n".join(weekList)),
            thumbnail_url="https://i.postimg.cc/HjNTcP6C/icon-7d-change.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Summary of " + ", ".join(nameList),
            input_message_content=InputTextMessageContent(
                "\n".join(valueList)
                + "\n\n"
                + "\n".join(capList)
                + "\n\n"
                + "\n".join(hourList)
                + "\n\n"
                + "\n".join(dayList)
                + "\n\n"
                + "\n".join(weekList)
                + "\n\n"
            ),
            thumbnail_url="https://i.postimg.cc/F7JNjgB2/icon-summary.jpg",
        ),
    ]
    logger.debug("Built %d inline results for multi-coin query", len(results))
    return results


def _build_single_coin_results(coin):
    logger.debug(
        "Building single-coin results for %s (id=%s)",
        getattr(coin, "symbol", None),
        getattr(coin, "id", None),
    )
    coinID = coin.id
    coinName = coin.name
    coinSymbol = coin.symbol
    coinPrice = coin.price + (" " + coin.currency if coin.price != "N/A" else "")
    coinCap = coin.market_cap + (
        " " + coin.currency if coin.market_cap != "N/A" else ""
    )
    coin1hr = coin.percent_change_1h + ("%" if coin.percent_change_1h != "N/A" else "")
    coin1day = coin.percent_change_24h + (
        "%" if coin.percent_change_24h != "N/A" else ""
    )
    coin7day = coin.percent_change_7d + ("%" if coin.percent_change_7d != "N/A" else "")

    imageURL = (
        "https://s2.coinmarketcap.com/static/img/coins/200x200/" + str(coinID) + ".png"
    )

    results = [
        InlineQueryResultPhoto(
            id=uuid4(),
            photo_url=(imageURL),
            thumbnail_url=(imageURL),
            title=coinName + "(" + coinSymbol + ")",
            caption=coinName + " (" + coinSymbol + ")",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Value: " + coinPrice,
            input_message_content=InputTextMessageContent(coinName + ": " + coinPrice),
            thumbnail_url="https://i.postimg.cc/JGBMbc2f/icon-values.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Market Capitalization: " + coinCap,
            input_message_content=InputTextMessageContent(
                coinName + " Market Capitalization: " + coinCap
            ),
            thumbnail_url="https://i.postimg.cc/YjPtGydB/icon-market-cap.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="One Hour Change: " + coin1hr,
            input_message_content=InputTextMessageContent(
                coinName + " One Hour Change: " + coin1hr
            ),
            thumbnail_url="https://i.postimg.cc/Cd2wB6cg/icon-1h-change.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="One Day Change: " + coin1day,
            input_message_content=InputTextMessageContent(
                coinName + " One Day Change: " + coin1day
            ),
            thumbnail_url="https://i.postimg.cc/RqYv6bXk/icon-1d-change.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Seven Day Change: " + coin7day,
            input_message_content=InputTextMessageContent(
                coinName + " Seven Day Change: " + coin7day
            ),
            thumbnail_url="https://i.postimg.cc/HjNTcP6C/icon-7d-change.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Summary of " + coinName + "(" + coinSymbol + ")",
            input_message_content=InputTextMessageContent(
                "---"
                + coinName
                + " Summary"
                + "("
                + coinSymbol
                + ")"
                + "---"
                + "\nPrice: "
                + coinPrice
                + "\nMarket Capitalization: "
                + coinCap
                + "\n1 hour percent change: "
                + coin1hr
                + "\n24 hour percent change: "
                + coin1day
                + "\n7 day percent change: "
                + coin7day
            ),
            thumbnail_url="https://i.postimg.cc/F7JNjgB2/icon-summary.jpg",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="AI summary",
            description="Generate an AI-written concise summary for this coin",
            input_message_content=InputTextMessageContent(
                f"AI summary for {coinName} ({coinSymbol}) - press the button below to generate an AI-written summary."
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "AI summary",
                            callback_data=f"ai_summary:{coinID}:{coin.currency}",
                        )
                    ]
                ]
            ),
            thumbnail_url="https://i.postimg.cc/YhmM1fPw/icon-ai-summary.jpg",
        ),
    ]
    return results
