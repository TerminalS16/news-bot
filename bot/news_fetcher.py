import feedparser
import requests

from bot.models import Source
from bot.schemas import Article

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NewsMyMindBot/1.0"}


def fetch_articles(source: Source) -> list[Article]:
    response = requests.get(source.url_or_query, headers=HEADERS, timeout=10)
    response.raise_for_status()

    parsed = feedparser.parse(response.content)

    articles = []
    for entry in parsed.entries:
        article = Article(
            title=entry.get("title", ""),
            url=entry.get("link", ""),
            content=entry.get("summary", ""),
            published_at=entry.get("published", ""),
        )
        articles.append(article)

    return articles