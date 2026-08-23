from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
import responses
from telegram import (
    CallbackQuery,
    InlineQuery,
    Message,
    Update,
    User,
)

import app


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("COINMARKETCAP_API_KEY", "fake-cmc-key")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")


@pytest_asyncio.fixture
async def telegram_app(mock_env):
    application = app.setup(webhook_url="https://fake.url")
    application.bot = AsyncMock()  # Mock the bot methods
    application.bot.id = 123456789
    await application.initialize()
    yield application
    await application.shutdown()


@pytest.fixture
def cmc_mock():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Mock Listings API
        rsps.add(
            responses.GET,
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map",
            json={
                "data": [
                    {"id": 1, "name": "Bitcoin", "symbol": "BTC"},
                    {"id": 1027, "name": "Ethereum", "symbol": "ETH"},
                    {"id": 74, "name": "Dogecoin", "symbol": "DOGE"},
                ]
            },
            status=200,
        )

        # Mock Quotes API for BTC and ETH
        rsps.add(
            responses.GET,
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
            match=[
                responses.matchers.query_param_matcher({"id": "1", "convert": "USD"})
            ],
            json={
                "data": {
                    "1": {
                        "id": 1,
                        "name": "Bitcoin",
                        "symbol": "BTC",
                        "quote": {
                            "USD": {
                                "price": 50000.0,
                                "market_cap": 1000000000.0,
                                "percent_change_1h": 1.0,
                                "percent_change_24h": 5.0,
                                "percent_change_7d": 10.0,
                            }
                        },
                    }
                }
            },
            status=200,
        )

        rsps.add(
            responses.GET,
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
            match=[
                responses.matchers.query_param_matcher(
                    {"id": "1,1027", "convert": "USD"}
                )
            ],
            json={
                "data": {
                    "1": {
                        "id": 1,
                        "name": "Bitcoin",
                        "symbol": "BTC",
                        "quote": {
                            "USD": {
                                "price": 50000.0,
                                "market_cap": 1000000000.0,
                                "percent_change_1h": 1.0,
                                "percent_change_24h": 5.0,
                                "percent_change_7d": 10.0,
                            }
                        },
                    },
                    "1027": {
                        "id": 1027,
                        "name": "Ethereum",
                        "symbol": "ETH",
                        "quote": {
                            "USD": {
                                "price": 3000.0,
                                "market_cap": 300000000.0,
                                "percent_change_1h": -1.0,
                                "percent_change_24h": -2.0,
                                "percent_change_7d": 5.0,
                            }
                        },
                    },
                }
            },
            status=200,
        )

        yield rsps


def create_inline_query_update(query: str) -> Update:
    update = MagicMock(spec=Update)
    update.inline_query = AsyncMock(spec=InlineQuery)
    update.inline_query.query = query
    user = User(id=1, first_name="Test", is_bot=False)
    update.inline_query.from_user = user
    return update


@pytest.mark.asyncio
async def test_single_coin_lookup(telegram_app, cmc_mock):
    update = create_inline_query_update("btc")
    await telegram_app.process_update(update)

    update.inline_query.answer.assert_called_once()
    args, kwargs = update.inline_query.answer.call_args
    results = args[0]

    assert len(results) > 0
    assert results[0].title == "Bitcoin(BTC)"
    assert "Bitcoin" in results[1].input_message_content.message_text


@pytest.mark.asyncio
async def test_multi_coin_lookup(telegram_app, cmc_mock):
    update = create_inline_query_update("btc,eth")
    await telegram_app.process_update(update)

    update.inline_query.answer.assert_called_once()
    args, kwargs = update.inline_query.answer.call_args
    results = args[0]

    assert len(results) > 0
    assert results[0].title == "Bitcoin (BTC), Ethereum (ETH)"
    assert "Bitcoin" in results[0].input_message_content.message_text
    assert "Ethereum" in results[0].input_message_content.message_text


@pytest.mark.asyncio
async def test_coin_ratio(telegram_app, cmc_mock):
    update = create_inline_query_update("btc/eth")
    await telegram_app.process_update(update)

    update.inline_query.answer.assert_called_once()
    args, kwargs = update.inline_query.answer.call_args
    results = args[0]

    assert len(results) > 0
    assert results[0].title == "btc / eth"
    assert "btc/eth" in results[0].input_message_content.message_text.lower()


@pytest.mark.asyncio
@patch("services.feedReader.feedparser.parse")
async def test_news_lookup(mock_parse, telegram_app):
    # Mock RSS feed response
    mock_parse.return_value = {
        "entries": [
            {
                "title": "Bitcoin reaches new heights",
                "link": "https://example.com/btc",
                "summary_detail": {"value": "Bitcoin went up today."},
            }
        ]
    }

    update = create_inline_query_update("news bitcoin")
    await telegram_app.process_update(update)

    update.inline_query.answer.assert_called_once()
    args, kwargs = update.inline_query.answer.call_args
    results = args[0]

    # Check that we got news articles returned
    assert len(results) > 0
    assert "Bitcoin reaches new heights" in results[0].title


@pytest.mark.asyncio
@patch("data.google_ai.litellm.completion")
async def test_ai_fallback(mock_litellm, telegram_app, cmc_mock):
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content='{"coins": ["BTC"], "news_keywords": ["SEC"]}')
        )
    ]

    mock_litellm.side_effect = [
        mock_response,  # First call: extracting JSON
        MagicMock(
            choices=[
                MagicMock(message=MagicMock(content="AI Response about SEC and BTC"))
            ]
        ),  # Second call: final answer
    ]

    update = create_inline_query_update("what did the SEC say about btc?")
    await telegram_app.process_update(update)

    update.inline_query.answer.assert_called_once()
    args, kwargs = update.inline_query.answer.call_args
    results = args[0]

    assert len(results) == 1
    assert results[0].id == "ai_fallback"
    assert results[0].title == "Ask AI ✨"


@pytest.mark.asyncio
@patch("data.google_ai.generate_text")
async def test_ai_summary_callback(mock_generate, telegram_app, cmc_mock):
    mock_generate.return_value = "Bitcoin is doing great!"

    update = MagicMock(spec=Update)
    update.inline_query = None
    update.message = None
    update.callback_query = AsyncMock(spec=CallbackQuery)
    update.callback_query.data = "ai_summary:1:USD"
    update.callback_query.message = MagicMock(spec=Message)

    await telegram_app.process_update(update)

    update.callback_query.answer.assert_any_call("Generating AI summary...")
    from telegram.constants import ParseMode

    update.callback_query.edit_message_text.assert_called_with(
        text="Bitcoin is doing great!", parse_mode=ParseMode.HTML
    )
