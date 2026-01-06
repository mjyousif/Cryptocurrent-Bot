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

    from api.inline_processor import InlineQueryProcessor

    processor = InlineQueryProcessor()
    try:
        results, cache_time = processor.build_results(query)
    except ValueError as e:
        logger.error("Error processing inline query: %s", e)
        await update.inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="Configuration error",
                    input_message_content=InputTextMessageContent(str(e)),
                    description="Error processing your request. Please try again later.",
                )
            ]
        )
        return

    if not results:
        await update.inline_query.answer([])
        return

    if cache_time:
        await update.inline_query.answer(results, cache_time=cache_time)
    else:
        await update.inline_query.answer(results)


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
