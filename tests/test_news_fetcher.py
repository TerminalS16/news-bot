from unittest.mock import patch, Mock
import pytest
import requests

from bot.models import Source
from bot.news_fetcher import fetch_articles


def test_fetch_articles_raises_on_network_failure():
    source = Source(type="rss", url_or_query="https://example.com/rss")

    with patch("bot.news_fetcher.requests.get", side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.Timeout):
            fetch_articles(source)


def test_fetch_articles_raises_on_http_error():
    source = Source(type="rss", url_or_query="https://example.com/rss")

    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

    with patch("bot.news_fetcher.requests.get", return_value=mock_response):
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_articles(source)


def test_fetch_articles_handles_empty_feed():
    source = Source(type="rss", url_or_query="https://example.com/rss")

    empty_rss = b"""<?xml version="1.0"?>
    <rss version="2.0"><channel><title>Empty</title></channel></rss>"""

    mock_response = Mock()
    mock_response.content = empty_rss
    mock_response.raise_for_status = Mock()

    with patch("bot.news_fetcher.requests.get", return_value=mock_response):
        result = fetch_articles(source)

    assert result == []


def test_fetch_articles_handles_missing_fields_gracefully():
    source = Source(type="rss", url_or_query="https://example.com/rss")

    broken_rss = """<?xml version="1.0"?>
    <rss version="2.0"><channel>
        <item><title>Только заголовок, без остального</title></item>
    </channel></rss>""".encode("utf-8")

    mock_response = Mock()
    mock_response.content = broken_rss
    mock_response.raise_for_status = Mock()

    with patch("bot.news_fetcher.requests.get", return_value=mock_response):
        result = fetch_articles(source)

    assert len(result) == 1
    assert result[0].title == "Только заголовок, без остального"
    assert result[0].url == ""