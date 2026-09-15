from bot.ai_processor import filter_and_format
from bot.models import Topic
from bot.schemas import Article
from llm_providers.base import LLMProvider


class StubProvider(LLMProvider):
    """Мок-провайдер: возвращает заранее заданный ответ вместо реального API."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.received_prompt: str | None = None

    def complete(self, prompt: str) -> str:
        self.received_prompt = prompt
        return self.response


def test_filter_and_format_returns_provider_response():
    topic = Topic(name="BTS", description="Новости о группе BTS.")
    articles = [Article(title="RM выпустил альбом", url="https://x.com/1", content="...", published_at="")]
    provider = StubProvider(response="RM выпустил новый альбом.")

    result = provider.complete("тест")  # проверка, что сам мок работает как ожидается

    block = filter_and_format(articles, topic, "briefly", provider)

    assert block.topic_name == "BTS"
    assert block.content_text == "RM выпустил новый альбом."


def test_prompt_includes_topic_name_and_article_titles():
    topic = Topic(name="Видеоигры", description="Крупные события индустрии.")
    articles = [Article(title="Вышла GTA 6", url="https://x.com/1", content="Подробности релиза", published_at="")]
    provider = StubProvider(response="что угодно")

    filter_and_format(articles, topic, "briefly", provider)

    assert "Видеоигры" in provider.received_prompt
    assert "Вышла GTA 6" in provider.received_prompt


def test_prompt_requires_russian_language():
    topic = Topic(name="BTS", description="Новости о группе BTS.")
    articles = [Article(title="Test", url="https://x.com/1", content="Test content", published_at="")]
    provider = StubProvider(response="что угодно")

    filter_and_format(articles, topic, "summary", provider)

    assert "на русском языке" in provider.received_prompt