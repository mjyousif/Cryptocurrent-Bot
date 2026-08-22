from unittest.mock import patch

from data.models import CryptoQuote
from services.crypto_service import (
    FormattedCrypto,
    _parse_query,
    get_coin_ratio,
    get_crypto_list,
)


def test_formatted_crypto_formatting():
    quote = CryptoQuote(
        id=1,
        name="Bitcoin",
        symbol="BTC",
        price=50000.1234,
        market_cap=1000000000.0,
        percent_change_1h=1.5,
        percent_change_24h=-2.5,
        percent_change_7d=10.0,
        currency="USD",
    )
    fc = FormattedCrypto(quote)
    assert fc.id == "1"
    assert fc.currency == "USD"
    assert fc.name == "Bitcoin"
    assert fc.symbol == "BTC"
    assert fc.price == "50,000.12"
    assert fc.market_cap == "1,000,000,000.00"
    assert fc.percent_change_1h == "1.5"


def test_formatted_crypto_small_price():
    quote = CryptoQuote(
        id=2,
        name="Shiba",
        symbol="SHIB",
        price=0.00001234,
        market_cap=None,
        percent_change_1h=None,
        percent_change_24h=None,
        percent_change_7d=None,
        currency="USD",
    )
    fc = FormattedCrypto(quote)
    assert fc.price == "0.000012"
    assert fc.market_cap == "N/A"
    assert fc.percent_change_1h == "N/A"


def test_parse_query():
    coins, currency, sort_type = _parse_query("bitcoin, ethereum")
    assert coins == ["bitcoin", "ethereum"]
    assert currency == "USD"
    assert sort_type == ""

    coins, currency, sort_type = _parse_query("btc eur 1d")
    assert coins == ["btc"]
    assert currency == "EUR"
    assert sort_type == "1d"

    coins, currency, sort_type = _parse_query("dogecoin price")
    assert coins == ["dogecoin"]
    assert currency == "USD"
    assert sort_type == "price"


@patch("services.crypto_service.CoinMarketCapClient")
def test_get_crypto_list(MockClient):
    mock_instance = MockClient.return_value
    mock_instance.get_listings.return_value = [
        {"id": 1, "name": "Bitcoin", "symbol": "BTC", "slug": "bitcoin"},
        {"id": 2, "name": "Ethereum", "symbol": "ETH", "slug": "ethereum"},
    ]

    # Need to mock the return of get_quotes
    # In crypto_service.py: quote = parse_coin_info(resp["data"][coin_id_str], currency)
    # The structure expected depends on parse_coin_info.
    # It's easier to mock parse_coin_info as well, or just return the structure it expects.
    # parse_coin_info expects the raw CMC quote data:
    # {"id": 1, "name": "Bitcoin", "symbol": "BTC", "quote": {"USD": {"price": 50000, ...}}}
    mock_instance.get_quotes.return_value = {
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
                        "percent_change_7d": 3.0,
                    }
                },
            }
        }
    }

    result = get_crypto_list("bitcoin")
    assert len(result) == 1
    assert result[0].name == "Bitcoin"
    assert result[0].symbol == "BTC"
    assert result[0].price == "50,000.00"


@patch("services.crypto_service.CoinMarketCapClient")
def test_get_crypto_list_not_found(MockClient):
    mock_instance = MockClient.return_value
    mock_instance.get_listings.return_value = []

    result = get_crypto_list("unknowncoin")
    assert result == []


@patch("services.crypto_service.CoinMarketCapClient")
def test_get_coin_ratio(MockClient):
    mock_instance = MockClient.return_value
    mock_instance.get_listings.return_value = [
        {"id": 1, "name": "Bitcoin", "symbol": "BTC", "slug": "bitcoin"},
        {"id": 2, "name": "Ethereum", "symbol": "ETH", "slug": "ethereum"},
    ]
    mock_instance.get_quotes.return_value = {
        "data": {
            "1": {"quote": {"USD": {"price": 60000.0}}},
            "2": {"quote": {"USD": {"price": 3000.0}}},
        }
    }

    ratio = get_coin_ratio("btc", "eth")
    assert ratio == "20"

    # Test not found
    ratio_unknown = get_coin_ratio("btc", "unknown")
    assert ratio_unknown is None
