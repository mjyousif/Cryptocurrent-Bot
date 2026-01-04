from telegram.ext import (
    Updater,
    CommandHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
)
from telegram import (
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
    Message,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# this stuff is for the webhook
import logging
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, MessageHandler, Filters

from uuid import uuid4
import os
from json_api import *
from feedReader import *
from sorter import *

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


def start(bot, update):
    try:  # this is what happens when user clicks the "sort button" in chat... at least what they should see
        if "_" in (update.message.text.split(" ")[1]):
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
            # update.message.reply_text('Please choose a sorting preference:',reply_markup=reply_markup)
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Please choose a sorting preference:",
                reply_markup=reply_markup,
            )
    except:
        bot.send_message(
            chat_id=update.message.chat_id,
            text=("Use me inline by tagging me and typing a crypto currency!"),
            # text=update.message.text
        )


def button(bot, update):
    query = update.inline_query
    bot.edit_message_text(
        text="Selected option",
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
    )


def inline_crypto(bot, update):
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
    elif "," in query:
        cryptoList = classifyQuery(query)
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
                thumb_url="https://i.imgur.com/R4ybbnJ.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title=cryptoList[0].currency + " Values",
                description="|".join(symbolValueList),
                input_message_content=InputTextMessageContent("\n".join(valueList)),
                thumb_url="https://i.imgur.com/My7IG7r.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title=cryptoList[0].currency + " Market Capitalizations",
                description="|".join(symbolCapList),
                input_message_content=InputTextMessageContent("\n".join(capList)),
                thumb_url="https://i.imgur.com/egncB1b.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Hour Changes",
                description="|".join(symbolHourList),
                input_message_content=InputTextMessageContent("\n".join(hourList)),
                thumb_url="https://i.imgur.com/pza5Xjb.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Day Changes",
                description="|".join(symbolDayList),
                input_message_content=InputTextMessageContent("\n".join(dayList)),
                thumb_url="https://i.imgur.com/98YM0PA.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Seven Day Changes",
                description="|".join(symbolWeekList),
                input_message_content=InputTextMessageContent("\n".join(weekList)),
                thumb_url="https://i.imgur.com/ZbPOM53.png",
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
                thumb_url="https://i.imgur.com/t6BPcMR.png",
            ),
        ]
        bot.answer_inline_query(
            update.inline_query.id, results
        )  # , switch_pm_text='Click for sorted results',switch_pm_parameter=cleanQuery)
    elif "/" in query:
        # Format the query to remove spaces that would mess up format
        query = query.replace("/", ",")
        cryptoList = classifyQuery(query)
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
                thumb_url="https://i.imgur.com/My7IG7r.png",
            ),
        ]

    else:

        # puts the query into a class that stores the coin and the currency
        coinList = classifyQuery(query)
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
                thumb_url=(imageURL),
                title=coinName + "(" + coinSymbol + ")",
                caption=coinName + " (" + coinSymbol + ")",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Value: " + coinPrice,
                input_message_content=InputTextMessageContent(
                    coinName + ": " + coinPrice
                ),
                thumb_url="https://i.imgur.com/My7IG7r.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Market Capitalization: " + coinCap,
                input_message_content=InputTextMessageContent(
                    coinName + " Market Capitalization: " + coinCap
                ),
                thumb_url="https://i.imgur.com/egncB1b.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Hour Change: " + coin1hr,
                input_message_content=InputTextMessageContent(
                    coinName + " One Hour Change: " + coin1hr
                ),
                thumb_url="https://i.imgur.com/pza5Xjb.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="One Day Change: " + coin1day,
                input_message_content=InputTextMessageContent(
                    coinName + " One Day Change: " + coin1day
                ),
                thumb_url="https://i.imgur.com/98YM0PA.png",
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Seven Day Change: " + coin7day,
                input_message_content=InputTextMessageContent(
                    coinName + " Seven Day Change: " + coin7day
                ),
                thumb_url="https://i.imgur.com/ZbPOM53.png",
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
                thumb_url="https://i.imgur.com/t6BPcMR.png",
            ),
        ]
    bot.answer_inline_query(update.inline_query.id, results, cache_time=300)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    if webhook_url:
        bot = Bot(TOKEN)
        update_queue = Queue()
        dp = Dispatcher(bot, update_queue)
    else:
        updater = Updater(TOKEN)
        bot = updater.bot
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(InlineQueryHandler(inline_crypto))
        dp.add_handler(InlineQueryHandler(button))
        # log all errors
        dp.add_error_handler(error)
    # Add your handlers here
    if webhook_url:
        bot.set_webhook(webhook_url=webhook_url)
        thread = Thread(target=dp.start, name="dispatcher")
        thread.start()
        return update_queue, bot
    else:
        bot.set_webhook()  # Delete webhook
        updater.start_polling()
        updater.idle()


if __name__ == "__main__":
    webhook_url = os.getenv("WEBHOOK_URL", None)
    setup(webhook_url=webhook_url if webhook_url else None)
