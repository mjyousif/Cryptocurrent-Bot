import pytest
import responses

from data.coinmarketcap import CoinMarketCapClient, parse_coin_info
from data.models import CryptoQuote


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("COINMARKETCAP_API_KEY", "test_key")


def test_client_init_no_key(monkeypatch):
    monkeypatch.delenv("COINMARKETCAP_API_KEY", raising=False)
    with pytest.raises(
        ValueError, match="COINMARKETCAP_API_KEY environment variable is not set"
    ):
        CoinMarketCapClient(api_key=None)


def test_client_init_with_key(mock_env):
    client = CoinMarketCapClient()
    assert client.api_key == "test_key"
    assert client._sess.headers["X-CMC_PRO_API_KEY"] == "test_key"


@responses.activate
def test_get_listings(mock_env):
    responses.add(
        responses.GET,
        "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map",
        json={"data": [{"id": 1, "name": "Bitcoin", "symbol": "BTC"}]},
        status=200,
    )

    client = CoinMarketCapClient()
    listings = client.get_listings()

    assert len(listings) == 1
    assert listings[0]["name"] == "Bitcoin"

    # Second call should be cached (responses library will fail if it tries to fetch again because only 1 mock response was added and responses library consumes them, or we can just assert cache)
    listings_cached = client.get_listings()
    assert listings == listings_cached


@responses.activate
def test_get_quotes(mock_env):
    responses.add(
        responses.GET,
        "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
        json={"data": {"1": {"id": 1, "name": "Bitcoin", "symbol": "BTC"}}},
        status=200,
    )

    client = CoinMarketCapClient()
    quotes = client.get_quotes([1], "USD")

    assert "1" in quotes["data"]
    assert quotes["data"]["1"]["name"] == "Bitcoin"


def test_parse_coin_info():
    raw_data = {
        "id": 1,
        "name": "Bitcoin",
        "symbol": "BTC",
        "quote": {
            "USD": {
                "price": 50000.5,
                "market_cap": 1000000.0,
                "percent_change_1h": 1.5,
                "percent_change_24h": -2.5,
                "percent_change_7d": 10.0,
            }
        },
    }

    quote = parse_coin_info(raw_data, "USD")

    assert isinstance(quote, CryptoQuote)
    assert quote.id == 1
    assert quote.name == "Bitcoin"
    assert quote.symbol == "BTC"
    assert quote.price == 50000.5
    assert quote.market_cap == 1000000.0
    assert quote.percent_change_1h == 1.5
    assert quote.percent_change_24h == -2.5
    assert quote.percent_change_7d == 10.0
