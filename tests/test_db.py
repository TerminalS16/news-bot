from dataclasses import dataclass

from bot.db import get_unsent_articles, mark_as_sent
from bot.models import User, Topic, UserTopic


@dataclass
class FakeArticle:
    url: str
    content_hash: str


def _create_user_topic(session) -> UserTopic:
    user = User(telegram_chat_id=111)
    topic = Topic(name="Тестовая тема")
    session.add_all([user, topic])
    session.commit()

    user_topic = UserTopic(user_id=user.id, topic_id=topic.id, depth_level="briefly")
    session.add(user_topic)
    session.commit()

    return user_topic


def test_all_articles_unsent_initially(db_session):
    user_topic = _create_user_topic(db_session)
    articles = [FakeArticle(url="https://example.com/1", content_hash="hash1")]

    result = get_unsent_articles(db_session, user_topic.id, articles)

    assert result == articles


def test_sent_articles_are_filtered_out(db_session):
    user_topic = _create_user_topic(db_session)
    articles = [
        FakeArticle(url="https://example.com/1", content_hash="hash1"),
        FakeArticle(url="https://example.com/2", content_hash="hash2"),
    ]

    mark_as_sent(db_session, user_topic.id, [articles[0]])
    result = get_unsent_articles(db_session, user_topic.id, articles)

    assert result == [articles[1]]


def test_dedup_is_scoped_to_user_topic(db_session):
    user_topic_a = _create_user_topic(db_session)

    # создаём второго пользователя и тему отдельно
    user_b = User(telegram_chat_id=222)
    topic_b = Topic(name="Другая тема")
    db_session.add_all([user_b, topic_b])
    db_session.commit()
    user_topic_b = UserTopic(user_id=user_b.id, topic_id=topic_b.id, depth_level="summary")
    db_session.add(user_topic_b)
    db_session.commit()

    article = FakeArticle(url="https://example.com/1", content_hash="hash1")

    mark_as_sent(db_session, user_topic_a.id, [article])

    result_a = get_unsent_articles(db_session, user_topic_a.id, [article])
    result_b = get_unsent_articles(db_session, user_topic_b.id, [article])

    assert result_a == []
    assert result_b == [article]