from bot.models import Topic
from bot.schemas import Article, DigestBlock
from llm_providers.base import LLMProvider


def _build_prompt(articles: list[Article], topic: Topic, depth_level: str) -> str:
    articles_text = "\n\n".join(
        f"Заголовок: {a.title}\nСсылка: {a.url}\nТекст: {a.content}"
        for a in articles
    )

    depth_instruction = {
        "summary": (
            "Дай подробную выжимку: ключевые детали, важные цитаты или выдержки "
            "из первоисточника, краткие пояснения и ссылки на источники."
        ),
        "briefly": (
            "Дай максимально сжатую сводку: суть каждой новости одной строкой, "
            "без лишних деталей."
        ),
    }[depth_level]

    return f"""Ты помогаешь собрать новостной дайджест по теме "{topic.name}".
Описание темы: {topic.description or "не указано"}.

Ниже приведены статьи, полученные из источников. Статьи могут быть на любом языке.

{articles_text}

Твоя задача:
1. Оставь только статьи, которые действительно относятся к теме "{topic.name}" и достаточно значимы.
2. Если несколько статей рассказывают об одном и том же событии — объедини их в одну запись, а не дублируй.
3. {depth_instruction}
4. Ответ должен быть полностью на русском языке, независимо от языка исходных статей.
5. Если после фильтрации не осталось релевантных статей — так и напиши: "Значимых новостей по теме не найдено".

Выведи только готовый текст дайджеста по этой теме, без дополнительных пояснений от себя."""


def filter_and_format(
    articles: list[Article],
    topic: Topic,
    depth_level: str,
    provider: LLMProvider,
) -> DigestBlock:
    prompt = _build_prompt(articles, topic, depth_level)
    result_text = provider.complete(prompt)

    return DigestBlock(topic_name=topic.name, content_text=result_text)