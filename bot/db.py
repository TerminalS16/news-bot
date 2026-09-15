from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from bot.config import settings
from bot.models import UserTopic, SentArticle

engine = create_engine(f"sqlite:///{settings.db_path}")
SessionLocal = sessionmaker(bind=engine)


def get_unsent_articles(session: Session, user_topic_id: int, articles: list) -> list:
    sent_urls = session.scalars(
        select(SentArticle.url).where(SentArticle.user_topic_id == user_topic_id)
    ).all()

    return [article for article in articles if article.url not in sent_urls]

def mark_as_sent(session: Session, user_topic_id: int, articles: list) -> None:
    for article in articles:
        sent_article = SentArticle(
            user_topic_id=user_topic_id,
            url=article.url,
            content_hash=article.content_hash,
        )
        session.add(sent_article)
    session.commit()