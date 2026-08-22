import pytest
from api import _build_multi_coin_results, _build_single_coin_results
from telegram import InlineQueryResultArticle, InlineQueryResultPhoto
from unittest.mock import MagicMock

class MockFormattedCrypto:
    def __init__(self):
        self.id = "1"
        self.name = "Bitcoin"
        self.symbol = "BTC"
        self.currency = "USD"
        self.price = "50,000"
        self.market_cap = "1,000,000"
        self.percent_change_1h = "1.0"
        self.percent_change_24h = "2.0"
        self.percent_change_7d = "3.0"

def test_build_multi_coin_results():
    coin1 = MockFormattedCrypto()
    coin2 = MockFormattedCrypto()
    coin2.id = "2"
    coin2.name = "Ethereum"
    coin2.symbol = "ETH"
    
    results = _build_multi_coin_results([coin1, coin2])
    
    # Check length and types of results
    assert len(results) == 7
    for res in results:
        assert isinstance(res, InlineQueryResultArticle)
        
    # Check that titles have combined coins
    assert results[0].title == "Bitcoin (BTC), Ethereum (ETH)"

def test_build_single_coin_results():
    coin = MockFormattedCrypto()
    
    results = _build_single_coin_results(coin)
    
    assert len(results) == 8
    assert isinstance(results[0], InlineQueryResultPhoto)
    assert isinstance(results[1], InlineQueryResultArticle)
    
    # Check AI Summary button callback data
    ai_summary_result = results[-1]
    assert ai_summary_result.title == "AI summary"
    
    # Check the keyboard markup inside the result
    keyboard = ai_summary_result.reply_markup.inline_keyboard
    assert keyboard[0][0].callback_data == "ai_summary:1:USD"
