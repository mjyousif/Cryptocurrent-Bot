from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram import (
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from api import _build_multi_coin_results, _build_single_coin_results

import logging

from uuid import uuid4
import os
from dotenv import load_dotenv
from services.crypto_service import get_crypto_list, get_coin_ratio
from feedReader import *
from sorter import *

# Load environment variables from .env file
load_dotenv()

# Configure logging level from environment (default INFO)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=LOG_LEVEL
)
logger = logging.getLogger(__name__)
logger.debug("Logger configured with level %s", LOG_LEVEL)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN environment variable is not set. "
        "Please set it in your .env file or as an environment variable."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:  # this is what happens when user clicks the "sort button" in chat... at least what they should see
        if update.message and "_" in (update.message.text.split(" ")[1]):
            # split and fix the query that was passed to be usable
            querySplit = update.message.text.split(" ")[1].split("_")
            query = ",".join(querySplit[:-1]) + " " + querySplit[-1]
            # present the inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Alphabetical", switch_inline_query=query + " " + "alpha"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Value", switch_inline_query=query + " " + "price"
                    ),
                    InlineKeyboardButton(
                        "Market Cap", switch_inline_query=query + " " + "mktcap"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Hour Change", switch_inline_query=query + " " + "1h"
                    ),
                    InlineKeyboardButton(
                        "Day Change", switch_inline_query=query + " " + "1d"
                    ),
                    InlineKeyboardButton(
                        "Week Change", switch_inline_query=query + " " + "7d"
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Please choose a sorting preference:",
                reply_markup=reply_markup,
            )
    except Exception:
        if update.message:
            await update.message.reply_text(
                "Use me inline by tagging me and typing a crypto currency!"
            )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # This handler seems unused/incomplete - keeping for compatibility
    if update.callback_query:
        await update.callback_query.answer()
        if update.callback_query.message:
            await update.callback_query.edit_message_text(text="Selected option")


def _build_single_coin_results(coin):
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
            thumbnail_url="https://i.imgur.com/My7IG7r.png",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Market Capitalization: " + coinCap,
            input_message_content=InputTextMessageContent(
                coinName + " Market Capitalization: " + coinCap
            ),
            thumbnail_url="https://i.imgur.com/egncB1b.png",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="One Hour Change: " + coin1hr,
            input_message_content=InputTextMessageContent(
                coinName + " One Hour Change: " + coin1hr
            ),
            thumbnail_url="https://i.imgur.com/pza5Xjb.png",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="One Day Change: " + coin1day,
            input_message_content=InputTextMessageContent(
                coinName + " One Day Change: " + coin1day
            ),
            thumbnail_url="https://i.imgur.com/98YM0PA.png",
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Seven Day Change: " + coin7day,
            input_message_content=InputTextMessageContent(
                coinName + " Seven Day Change: " + coin7day
            ),
            thumbnail_url="https://i.imgur.com/ZbPOM53.png",
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
            thumbnail_url="https://i.imgur.com/t6BPcMR.png",
        ),
    ]
    return results


async def inline_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.inline_query:
        return
    query = update.inline_query.query
    if not query:
        return
    newsQuery = query.split(" ")
    if newsQuery[0].lower() == "news":
        if len(newsQuery) == 1:
            newsArticles = news()
        else:
            j = 0
            for j in range(len(newsQuery) - 2):
                newsQuery[1] = newsQuery[1] + " " + newsQuery[2]
                del newsQuery[2]
            newsArticles = news(newsQuery[1])
        results = []
        i = 0
        for i in range(len(newsArticles)):
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=newsArticles[i].title,
                    input_message_content=InputTextMessageContent(newsArticles[i].link),
                    description=newsArticles[i].description,
                )
            )
        await update.inline_query.answer(results)
        return
    elif "," in query:
        try:
            cryptoList = get_crypto_list(query)
        except ValueError as e:
            logger.error("Error fetching crypto list: %s", e)
            await update.inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title="Configuration error",
                        input_message_content=InputTextMessageContent(str(e)),
                        description="Please set COINMARKETCAP_API_KEY in your .env or environment",
                    )
                ]
            )
            return
        # If no coins were found, return empty results
        if not cryptoList:
            await update.inline_query.answer([])
            return

        # Build and send results for multi-coin query
        results = _build_multi_coin_results(cryptoList)
        logger.debug("Answering inline with %d multi-coin results", len(results))
        await update.inline_query.answer(results)
        return
    elif "/" in query:
        # Format the query to coin1/coin2 and use service helper to compute ratio
        parts = [p.strip() for p in query.split("/") if p.strip()]
        if len(parts) != 2:
            await update.inline_query.answer([])
            return
        try:
            ratio = get_coin_ratio(parts[0], parts[1])
        except ValueError as e:
            logger.error("Error computing ratio: %s", e)
            await update.inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title="Configuration error",
                        input_message_content=InputTextMessageContent(str(e)),
                        description="Please set COINMARKETCAP_API_KEY in your .env or environment",
                    )
                ]
            )
            return
        if not ratio:
            await update.inline_query.answer([])
            return

        # Build result from ratio
        title = f"{parts[0]} / {parts[1]}"
        description = f"{ratio} {parts[0].upper()}/{parts[1].upper()}"
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(f"{description}"),
                thumbnail_url="https://i.imgur.com/My7IG7r.png",
            ),
        ]
        await update.inline_query.answer(results)
        return

    else:

        # Single coin query: use service to get a formatted crypto object
        try:
            cryptoList = get_crypto_list(query)
        except ValueError as e:
            logger.error("Error fetching crypto list: %s", e)
            await update.inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title="Configuration error",
                        input_message_content=InputTextMessageContent(str(e)),
                        description="Please set COINMARKETCAP_API_KEY in your .env or environment",
                    )
                ]
            )
            return
        # If no coins were found, return empty results
        if not cryptoList:
            await update.inline_query.answer([])
            return

        coin = cryptoList[0]
        results = _build_single_coin_results(coin)
        await update.inline_query.answer(results, cache_time=300)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    # Create application
    application = Application.builder().token(TOKEN).build()
    logger.info("Application created; registering handlers")

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_crypto))
    application.add_handler(CallbackQueryHandler(button))

    # Register error handler
    application.add_error_handler(error_handler)
    logger.debug("Handlers registered")

    # Set up webhook or polling
    if webhook_url:
        # For webhook mode, return the application to be used with a web framework
        return application
    else:
        # run_polling() manages its own event loop, so we don't need asyncio.run()
        # It's a blocking call that will run until stopped
        logger.info("Starting polling")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    webhook_url = os.getenv("WEBHOOK_URL", None)
    if webhook_url:
        # For webhook mode, you'd typically run this in a web server context
        # This is a placeholder - adjust based on your deployment needs
        app = setup(webhook_url=webhook_url)
        # In webhook mode, you'd typically set up a web server here
        # For now, this just returns the application
    else:
        # run_polling() handles the event loop internally
        setup()
