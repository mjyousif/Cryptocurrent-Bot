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

import logging

from uuid import uuid4
import os
from dotenv import load_dotenv
from json_api import *
from feedReader import *
from sorter import *

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        cryptoList = classifyQuery(query)
        # If no coins were found, return empty results
        if not cryptoList:
            await update.inline_query.answer([])
            return
        # stuff that will go in the results, prepared up here because I can't do it in their respective results
        # Ternarys to remove things that wouldn't make sense in certain conditions. Like if the data is 'N/A', I don't want the currency to show
        # The big loop gets the data in a list which is joined however it needs to be in the results
        nameList = []
        symbolList = []
        valueList = ["Values:"]
        symbolValueList = []
        capList = ["Market Caps:"]
        symbolCapList = []
        hourList = ["1 Hour Changes:"]
        symbolHourList = []
        dayList = ["1 Day Changes:"]
        symbolDayList = []
        weekList = ["7 Day Changes:"]
        symbolWeekList = []

        k = 0
        for k in range(len(cryptoList)):
            nameList.append(cryptoList[k].name + " (" + cryptoList[k].symbol + ")")
            symbolList.append(cryptoList[k].symbol)

            valueList.append(
                cryptoList[k].name
                + " ("
                + cryptoList[k].symbol
                + "): "
                + cryptoList[k].price
                + " "
                + (cryptoList[k].currency if cryptoList[k].price != "N/A" else "")
            )
            symbolValueList.append(
                cryptoList[k].symbol
                + ": "
                + cryptoList[k].price
                + " "
                + (cryptoList[k].currency if cryptoList[k].price != "N/A" else "")
            )

            capList.append(
                cryptoList[k].name
                + " ("
                + cryptoList[k].symbol
                + "): "
                + cryptoList[k].market_cap
                + " "
                + (cryptoList[k].currency if cryptoList[k].market_cap != "N/A" else "")
            )
            symbolCapList.append(
                cryptoList[k].symbol
                + ": "
                + cryptoList[k].market_cap
                + " "
                + (cryptoList[k].currency if cryptoList[k].market_cap != "N/A" else "")
            )

            hourList.append(
                cryptoList[k].name
                + " ("
                + cryptoList[k].symbol
                + "): "
                + cryptoList[k].percent_change_1h
                + "%"
            )
            symbolHourList.append(
                cryptoList[k].symbol + ": " + cryptoList[k].percent_change_1h + "%"
            )

            dayList.append(
                cryptoList[k].name
                + " ("
                + cryptoList[k].symbol
                + "): "
                + cryptoList[k].percent_change_24h
                + "%"
            )
            symbolDayList.append(
                cryptoList[k].symbol + ": " + cryptoList[k].percent_change_24h + "%"
            )

            weekList.append(
                cryptoList[k].name
                + " ("
                + cryptoList[k].symbol
                + "): "
                + cryptoList[k].percent_change_7d
                + "%"
            )
            symbolWeekList.append(
                cryptoList[k].symbol + ": " + cryptoList[k].percent_change_7d + "%"
            )

        # cleanQuery="_".join(symbolList)+"_"+classifiedQuery.currency
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title=", ".join(nameList),
                input_message_content=InputTextMessageContent("\n".join(nameList)),
                thumbnail_url="https://i.imgur.com/R4ybbnJ.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title=cryptoList[0].currency + " Values",
                description="|".join(symbolValueList),
                input_message_content=InputTextMessageContent("\n".join(valueList)),
                thumbnail_url="https://i.imgur.com/My7IG7r.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title=cryptoList[0].currency + " Market Capitalizations",
                description="|".join(symbolCapList),
                input_message_content=InputTextMessageContent("\n".join(capList)),
                thumbnail_url="https://i.imgur.com/egncB1b.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Hour Changes",
                description="|".join(symbolHourList),
                input_message_content=InputTextMessageContent("\n".join(hourList)),
                thumbnail_url="https://i.imgur.com/pza5Xjb.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Day Changes",
                description="|".join(symbolDayList),
                input_message_content=InputTextMessageContent("\n".join(dayList)),
                thumbnail_url="https://i.imgur.com/98YM0PA.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Seven Day Changes",
                description="|".join(symbolWeekList),
                input_message_content=InputTextMessageContent("\n".join(weekList)),
                thumbnail_url="https://i.imgur.com/ZbPOM53.png",
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
                thumbnail_url="https://i.imgur.com/t6BPcMR.png",
            ),
        ]
        await update.inline_query.answer(results)
    elif "/" in query:
        # Format the query to remove spaces that would mess up format
        query = query.replace("/", ",")
        cryptoList = classifyQuery(query)
        # Need at least 2 coins for division
        if len(cryptoList) < 2:
            await update.inline_query.answer([])
            return
        coin1Data = cryptoList[0]
        coin2Data = cryptoList[1]
        coin1Name = cryptoList[0].name
        coin1Symbol = cryptoList[0].symbol
        coin1Value = cryptoList[0].price
        coin2Name = cryptoList[1].name
        coin2Symbol = cryptoList[1].symbol
        coin2Value = cryptoList[1].price
        # If the value for the coin is not available, return none so that nothing is returned to the user.
        if coin1Value == "N/A" or coin2Value == "N/A":
            coin1InCoin2 = None
        # Do some manipulation. Turn the string from the data into float to do the math to get the value and return to string. Limit the value to 8 places past the decimal. Comma separate the left side of the number.
        else:
            coin1InCoin2 = str(
                float(coin1Value.replace(",", "")) / float(coin2Value.replace(",", ""))
            )
            coin1InCoin2 = coin1InCoin2[: coin1InCoin2.find(".") + 9]
            coin1InCoin2 = "{:,}".format(
                float(
                    coin1InCoin2[: coin1InCoin2.find(".")]
                    + "."
                    + coin1InCoin2[coin1InCoin2.find(".") + 1 :]
                )
            )

        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title=coin1Name
                + " ("
                + coin1Symbol
                + ") / "
                + coin2Name
                + " ("
                + coin2Symbol
                + ")",
                description=coin1InCoin2 + " " + coin1Symbol + "/" + coin2Symbol,
                input_message_content=InputTextMessageContent(
                    coin1InCoin2
                    + " "
                    + coin1Name
                    + " ("
                    + coin1Symbol
                    + ") / "
                    + coin2Name
                    + " ("
                    + coin2Symbol
                    + ")"
                ),
                thumbnail_url="https://i.imgur.com/My7IG7r.png",
            ),
        ]
        await update.inline_query.answer(results)
        return

    else:

        # puts the query into a class that stores the coin and the currency
        coinList = classifyQuery(query)
        # If no coins were found, return empty results
        if not coinList:
            await update.inline_query.answer([])
            return
        # getCoinData(classifiedQuery.coinQuery[0],classifiedQuery.currency)
        coinID = coinList[0].id
        coinName = coinList[0].name
        coinSymbol = coinList[0].symbol
        coinPrice = (
            coinList[0].price
            + " "
            + (coinList[0].currency if coinList[0].price != "N/A" else "")
        )
        coinCap = (
            coinList[0].market_cap
            + " "
            + (coinList[0].currency if coinList[0].market_cap != "N/A" else "")
        )
        coin1hr = coinList[0].percent_change_1h + (
            "%" if coinList[0].percent_change_1h != "N/A" else ""
        )
        coin1day = coinList[0].percent_change_24h + (
            "%" if coinList[0].percent_change_24h != "N/A" else ""
        )
        coin7day = coinList[0].percent_change_7d + (
            "%" if coinList[0].percent_change_7d != "N/A" else ""
        )
        imageURL = (
            "https://s2.coinmarketcap.com/static/img/coins/200x200/"
            + str(coinID)
            + ".png"
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
                input_message_content=InputTextMessageContent(
                    coinName + ": " + coinPrice
                ),
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
        await update.inline_query.answer(results, cache_time=300)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    # Create application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_crypto))
    application.add_handler(CallbackQueryHandler(button))

    # Register error handler
    application.add_error_handler(error_handler)

    # Set up webhook or polling
    if webhook_url:
        # For webhook mode, return the application to be used with a web framework
        return application
    else:
        # run_polling() manages its own event loop, so we don't need asyncio.run()
        # It's a blocking call that will run until stopped
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
