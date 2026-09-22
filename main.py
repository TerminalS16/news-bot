import asyncio
import logging
from functools import partial

from aiogram import Bot, Dispatcher
from sqlalchemy import select

from bot.config import settings
from bot.handlers import router
from bot.scheduler import setup_scheduler
from bot.db import SessionLocal, get_unsent_articles, mark_as_sent
from bot.models import User, UserTopic, Topic, Source
from bot.news_fetcher import fetch_articles
from bot.ai_processor import filter_and_format
from bot.digest_builder import format_block, split_into_messages
from llm_providers.anthropic_provider import AnthropicProvider
from llm_providers.base import LLMProvider


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_digest_for_user(bot: Bot, provider: LLMProvider, user_id: int) -> None:
    session = SessionLocal()
    user = session.get(User, user_id)

    if user is None or user.is_paused:
        session.close()
        return

    chat_id = user.telegram_chat_id  # забираем значение, пока сессия ещё активна

    user_topics = session.scalars(
        select(UserTopic).where(UserTopic.user_id == user_id, UserTopic.is_active == True)
    ).all()


    blocks = []
    for ut in user_topics:
        topic = session.get(Topic, ut.topic_id)
        sources = session.scalars(
            select(Source).where(Source.topic_id == topic.id, Source.is_active == True)
        ).all()

        all_articles = []
        for source in sources:
            try:
                all_articles.extend(fetch_articles(source))
            except Exception as e:
                logger.warning(f"Не удалось получить статьи из источника {source.url_or_query}: {e}")

        unsent = get_unsent_articles(session, ut.id, all_articles)
        if not unsent:
            blocks.append(DigestBlock(topic_name=topic.name, content_text="Новых новостей нет."))
            continue

        block = filter_and_format(unsent, topic, ut.depth_level, provider)
        blocks.append(block)
        mark_as_sent(session, ut.id, unsent)

    session.close()

    if not blocks:
        await bot.send_message(chat_id, "Сегодня нет тем для дайджеста.")
    else:
        for block in blocks:
            full_text = format_block(block)
            for chunk in split_into_messages(full_text):
                try:
                    await bot.send_message(chat_id, chunk, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Не удалось отправить часть дайджеста (тема: {block.topic_name}): {e}")

    logger.info(f"Дайджест отправлен user_id={user_id}")


async def main() -> None:
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    provider = AnthropicProvider()
    job_func = partial(send_digest_for_user, bot, provider)
    scheduler = setup_scheduler(job_func)
    scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")