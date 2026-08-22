from unittest.mock import MagicMock, patch

from telegram import InlineQueryResultArticle

from api.inline_processor import InlineQueryProcessor


@patch("api.inline_processor.news")
def test_build_results_news(mock_news):
    mock_news.return_value = [
        MagicMock(title="News 1", link="http://news1", description="Desc 1")
    ]
    processor = InlineQueryProcessor()

    results, cache_time = processor.build_results("news bitcoin")

    mock_news.assert_called_once_with("bitcoin")
    assert len(results) == 1
    assert isinstance(results[0], InlineQueryResultArticle)
    assert results[0].title == "News 1"
    assert results[0].description == "Desc 1"
    assert cache_time is None


@patch("api.inline_processor.news")
def test_build_results_news_no_tag(mock_news):
    mock_news.return_value = []
    processor = InlineQueryProcessor()

    results, cache_time = processor.build_results("news")

    mock_news.assert_called_once_with()
    assert len(results) == 0


@patch("api.inline_processor.get_crypto_list")
@patch("api.inline_processor._build_multi_coin_results")
def test_build_results_multi_coin(mock_build_multi, mock_get_crypto):
    mock_get_crypto.return_value = ["mock_coin_1", "mock_coin_2"]
    mock_build_multi.return_value = ["mock_result"]
    processor = InlineQueryProcessor()

    results, cache_time = processor.build_results("btc,eth")

    mock_get_crypto.assert_called_once_with("btc,eth")
    mock_build_multi.assert_called_once_with(["mock_coin_1", "mock_coin_2"])
    assert results == ["mock_result"]
    assert cache_time is None


@patch("api.inline_processor.get_coin_ratio")
def test_build_results_ratio(mock_get_ratio):
    mock_get_ratio.return_value = "20.5"
    processor = InlineQueryProcessor()

    results, cache_time = processor.build_results("btc/eth")

    mock_get_ratio.assert_called_once_with("btc", "eth")
    assert len(results) == 1
    assert isinstance(results[0], InlineQueryResultArticle)
    assert results[0].title == "btc / eth"
    assert "20.5 BTC/ETH" in results[0].description
    assert cache_time is None


@patch("api.inline_processor.get_crypto_list")
@patch("api.inline_processor._build_single_coin_results")
def test_build_results_single_coin(mock_build_single, mock_get_crypto):
    mock_get_crypto.return_value = ["mock_coin_1"]
    mock_build_single.return_value = ["mock_result"]
    processor = InlineQueryProcessor()

    results, cache_time = processor.build_results("btc")

    mock_get_crypto.assert_called_once_with("btc")
    mock_build_single.assert_called_once_with("mock_coin_1")
    assert results == ["mock_result"]
    assert cache_time == 300


def test_build_results_empty():
    processor = InlineQueryProcessor()
    results, cache_time = processor.build_results("")
    assert results == []
    assert cache_time is None
