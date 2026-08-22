from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
    ChosenInlineResultHandler,
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
from services.feedReader import *
from services.sorter import *

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



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Use me inline by tagging me and typing a crypto currency!"
        )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query:
        return

    data_payload = update.callback_query.data or ""

    # Handle AI summary callbacks: format: ai_summary:<coin_id>:<currency>
    if data_payload.startswith("ai_summary:"):
        # Acknowledge the callback (shows a small popup)
        await update.callback_query.answer("Generating AI summary...")
        parts = data_payload.split(":")
        if len(parts) < 3:
            await update.callback_query.edit_message_text(
                "Invalid AI summary request data."
            )
            return
        coin_id = parts[1]
        currency = parts[2]

        try:
            # Fetch latest quote from CoinMarketCap
            from data.coinmarketcap import CoinMarketCapClient, parse_coin_info
            from data.google_ai import generate_text, GoogleAIError

            client = CoinMarketCapClient()
            resp = client.get_quotes([int(coin_id)], currency)
            if "data" not in resp or str(coin_id) not in resp["data"]:
                await update.callback_query.edit_message_text(
                    "Unable to fetch coin data for AI summary."
                )
                return

            quote = parse_coin_info(resp["data"][str(coin_id)], currency)

            prompt = (
                f"Write a bombastic and truthful 2-3 sentence market summary for {quote.name} ({quote.symbol}). "
                f"Use the data below and be fun and informational.\n"
                f"Price: {quote.price} {quote.currency}\n"
                f"Market cap: {quote.market_cap} {quote.currency}\n"
                f"1h change: {quote.percent_change_1h}%\n"
                f"24h change: {quote.percent_change_24h}%\n"
                f"7d change: {quote.percent_change_7d}%\n"
                f"Do speculate (either way) and provide investment advice."
            )

            # Telegram MarkdownV2 examples to include in the instruction so the LLM outputs compatible markup
            formatting_notes = (
                "Do not use any formatting, return plain text and emojis only."
            )

            full_prompt = prompt + "\n\n" + formatting_notes

            try:
                generated = generate_text(
                    full_prompt, temperature=0.2, max_output_tokens=120
                )
            except GoogleAIError as e:
                await update.callback_query.edit_message_text(
                    f"AI generation failed: {e}"
                )
                return

            # Log the generated AI response (truncated to 300 chars)
            try:
                log_preview = (
                    generated if len(generated) <= 300 else generated[:300] + "..."
                )
            except Exception:
                log_preview = "<unavailable>"
            logger.info(
                "AI summary generated for %s (id=%s): %s",
                quote.name,
                coin_id,
                log_preview,
            )

            # Edit the original message with the generated text, but avoid editing if content is identical
            current_msg = update.callback_query.message
            try:
                if current_msg and getattr(current_msg, "text", None) == generated:
                    # Message already has same content; notify user and skip edit
                    await update.callback_query.answer("Already up to date.")
                else:
                    await update.callback_query.edit_message_text(generated)
            except Exception as exc:
                # Ignore 'Message is not modified' errors (no change)
                if "Message is not modified" in str(exc):
                    logger.info("Skipping edit; message already has same content.")
                    await update.callback_query.answer("Already up to date.")
                else:
                    logger.exception("Failed to edit message: %s", exc)
                    try:
                        await update.callback_query.edit_message_text(
                            "Failed to post AI summary due to formatting issues."
                        )
                    except Exception:
                        logger.exception(
                            "Failed to post fallback error message for AI summary"
                        )
        except Exception as exc:
            logger.exception("AI summary callback failed: %s", exc)
            await update.callback_query.edit_message_text(
                "Failed to generate AI summary. Please try again later."
            )
        return

    # Default fallback behaviour for other callbacks
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


async def handle_chosen_inline_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.chosen_inline_result:
        return
        
    result_id = update.chosen_inline_result.result_id
    query = update.chosen_inline_result.query
    inline_message_id = update.chosen_inline_result.inline_message_id
    
    if result_id == "ai_fallback" and inline_message_id:
        from services.ai_fallback import process_ai_query
        try:
            # Process the query using our new AI fallback service
            response_text = await process_ai_query(query)
            
            # Edit the original "Thinking..." message
            await context.bot.edit_message_text(
                inline_message_id=inline_message_id,
                text=response_text
            )
        except Exception as e:
            logger.error("Failed to process chosen inline result for AI: %s", e)
            try:
                await context.bot.edit_message_text(
                    inline_message_id=inline_message_id,
                    text="Sorry, I encountered an error while analyzing your request."
                )
            except Exception:
                pass


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    if not TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN environment variable is not set. "
            "Please set it in your .env file or as an environment variable."
        )

    # Create application
    application = Application.builder().token(TOKEN).build()
    logger.info("Application created; registering handlers")

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_crypto))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(ChosenInlineResultHandler(handle_chosen_inline_result))

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
