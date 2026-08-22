import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from telegram import Update, InlineQuery, CallbackQuery, Message, InlineQueryResultArticle, User, Chat
import app
import os

@pytest.mark.asyncio
async def test_start_command():
    update = MagicMock(spec=Update)
    update.message = AsyncMock(spec=Message)
    context = MagicMock()
    
    await app.start(update, context)
    update.message.reply_text.assert_called_once_with(
        "Use me inline by tagging me and typing a crypto currency!"
    )

@pytest.mark.asyncio
@patch('api.inline_processor.InlineQueryProcessor')
async def test_inline_crypto_empty_query(mock_processor):
    update = MagicMock(spec=Update)
    update.inline_query = MagicMock(spec=InlineQuery)
    update.inline_query.query = ""
    context = MagicMock()
    
    await app.inline_crypto(update, context)
    mock_processor.return_value.build_results.assert_not_called()

@pytest.mark.asyncio
@patch('api.inline_processor.InlineQueryProcessor')
async def test_inline_crypto_valid_query(mock_processor):
    update = MagicMock(spec=Update)
    update.inline_query = AsyncMock(spec=InlineQuery)
    update.inline_query.query = "btc"
    context = MagicMock()
    
    processor_instance = mock_processor.return_value
    processor_instance.build_results.return_value = (["mock_result"], 300)
    
    await app.inline_crypto(update, context)
    
    processor_instance.build_results.assert_called_once_with("btc")
    update.inline_query.answer.assert_called_once_with(["mock_result"], cache_time=300)

@pytest.mark.asyncio
async def test_button_no_callback_query():
    update = MagicMock(spec=Update)
    update.callback_query = None
    context = MagicMock()
    
    await app.button(update, context)
    # Should just return

@pytest.mark.asyncio
async def test_button_default_fallback():
    update = MagicMock(spec=Update)
    update.callback_query = AsyncMock(spec=CallbackQuery)
    update.callback_query.data = "other_callback"
    update.callback_query.message = MagicMock(spec=Message)
    context = MagicMock()
    
    await app.button(update, context)
    
    update.callback_query.answer.assert_called_once()
    update.callback_query.edit_message_text.assert_called_once_with(text="Selected option")

@pytest.mark.asyncio
@patch('data.coinmarketcap.CoinMarketCapClient')
@patch('data.google_ai.generate_text')
async def test_button_ai_summary(mock_generate, MockClient):
    update = MagicMock(spec=Update)
    update.callback_query = AsyncMock(spec=CallbackQuery)
    update.callback_query.data = "ai_summary:1:USD"
    update.callback_query.message = MagicMock(spec=Message)
    context = MagicMock()
    
    mock_client_instance = MockClient.return_value
    mock_client_instance.get_quotes.return_value = {
        "data": {
            "1": {
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "quote": {
                    "USD": {
                        "price": 50000.0,
                        "market_cap": 1000000.0,
                        "percent_change_1h": 1.0,
                        "percent_change_24h": 2.0,
                        "percent_change_7d": 3.0
                    }
                }
            }
        }
    }
    mock_generate.return_value = "Bitcoin is doing great today!"
    
    await app.button(update, context)
    
    update.callback_query.answer.assert_any_call("Generating AI summary...")
    update.callback_query.edit_message_text.assert_called_with("Bitcoin is doing great today!")
