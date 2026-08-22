import pytest
from unittest.mock import patch
from services.feedReader import news, Articles, getBetween

def test_getBetween():
    text = "Hello <p>world</p> today"
    result = getBetween(text, "<p>", "</p>", beforeFix=3, afterFix=0)
    assert result == "world"

@patch('services.feedReader.feedparser.parse')
def test_news_without_tag(mock_parse):
    # Setup mock return value
    mock_feed = {
        "entries": [
            {
                "title": "Crypto is booming",
                "link": "http://example.com/crypto",
                "summary_detail": {"value": "The market is up today."}
            }
        ]
    }
    mock_parse.return_value = mock_feed
    
    results = news()
    
    # 3 feeds are fetched in the code, so we should get 3 duplicates of our mock data
    assert len(results) == 3
    assert isinstance(results[0], Articles)
    assert results[0].title == "Crypto is booming"
    assert results[0].link == "http://example.com/crypto"
    assert results[0].description == "The market is up today."

@patch('services.feedReader.feedparser.parse')
def test_news_with_tag(mock_parse):
    # Setup mock return value
    mock_feed_coindesk = {
        "entries": [
            {
                "title": "Bitcoin news",
                "link": "http://coindesk.com/btc",
                "summary_detail": {"value": "BTC goes up."},
                "tags": [{"term": "Bitcoin"}]
            },
            {
                "title": "Ethereum news",
                "link": "http://coindesk.com/eth",
                "summary_detail": {"value": "ETH goes up."},
                "tags": [{"term": "Ethereum"}]
            }
        ]
    }
    mock_parse.return_value = mock_feed_coindesk
    
    results = news(tag="bitcoin")
    
    # Since all 3 urls are mocked to return the same thing, we get 3 matches.
    # Note: feedReader.py parses tags and checks for term.lower()
    assert len(results) == 3
    assert results[0].title == "Bitcoin news"
    
def test_article_class():
    article = Articles("Title", "http://link", "Desc")
    assert article.title == "Title"
    assert article.link == "http://link"
    assert article.description == "Desc"
