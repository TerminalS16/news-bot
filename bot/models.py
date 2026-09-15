from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_chat_id: Mapped[int] = mapped_column(Integer, unique=True)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    schedules: Mapped[list["Schedule"]] = relationship(back_populates="user")
    user_topics: Mapped[list["UserTopic"]] = relationship(back_populates="user")


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    time: Mapped[str] = mapped_column(String)
    timezone: Mapped[str] = mapped_column(String)
    frequency: Mapped[str] = mapped_column(String, default="daily")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="schedules")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    sources: Mapped[list["Source"]] = relationship(back_populates="topic")
    user_topics: Mapped[list["UserTopic"]] = relationship(back_populates="topic")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    type: Mapped[str] = mapped_column(String)
    url_or_query: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    topic: Mapped["Topic"] = relationship(back_populates="sources")


class UserTopic(Base):
    __tablename__ = "user_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    depth_level: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="user_topics")
    topic: Mapped["Topic"] = relationship(back_populates="user_topics")
    sent_articles: Mapped[list["SentArticle"]] = relationship(back_populates="user_topic")


class SentArticle(Base):
    __tablename__ = "sent_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_topic_id: Mapped[int] = mapped_column(ForeignKey("user_topics.id"))
    url: Mapped[str] = mapped_column(String)
    content_hash: Mapped[str] = mapped_column(String)
    sent_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user_topic: Mapped["UserTopic"] = relationship(back_populates="sent_articles")