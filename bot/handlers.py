from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from bot.db import SessionLocal
from bot.models import User, UserTopic, Topic

router = Router()


def _get_or_create_user(chat_id: int) -> User:
    session = SessionLocal()
    user = session.scalar(select(User).where(User.telegram_chat_id == chat_id))

    if user is None:
        user = User(telegram_chat_id=chat_id)
        session.add(user)
        session.commit()

    session.refresh(user)
    session.close()
    return user


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    user = _get_or_create_user(message.chat.id)
    await message.answer(
        "Привет! Я собираю для тебя новостной дайджест по заданным темам.\n"
        "Используй /topics — посмотреть список тем.\n"
        "Используй /pause и /resume — остановить или возобновить рассылку."
    )


@router.message(Command("topics"))
async def topics_handler(message: Message) -> None:
    user = _get_or_create_user(message.chat.id)

    session = SessionLocal()
    user_topics = session.scalars(
        select(UserTopic).where(UserTopic.user_id == user.id, UserTopic.is_active == True)
    ).all()

    if not user_topics:
        await message.answer("У тебя пока нет активных тем.")
        session.close()
        return

    lines = []
    for ut in user_topics:
        topic = session.get(Topic, ut.topic_id)
        lines.append(f"— {topic.name} (глубина: {ut.depth_level})")

    session.close()
    await message.answer("Твои темы:\n" + "\n".join(lines))


@router.message(Command("pause"))
async def pause_handler(message: Message) -> None:
    session = SessionLocal()
    user = session.scalar(select(User).where(User.telegram_chat_id == message.chat.id))

    if user is None:
        await message.answer("Сначала используй /start.")
        session.close()
        return

    user.is_paused = True
    session.commit()
    session.close()
    await message.answer("Рассылка приостановлена. Используй /resume, чтобы возобновить.")


@router.message(Command("resume"))
async def resume_handler(message: Message) -> None:
    session = SessionLocal()
    user = session.scalar(select(User).where(User.telegram_chat_id == message.chat.id))

    if user is None:
        await message.answer("Сначала используй /start.")
        session.close()
        return

    user.is_paused = False
    session.commit()
    session.close()
    await message.answer("Рассылка возобновлена.")


@router.message()
async def echo_handler(message: Message) -> None:
    await message.answer(f"Вы написали: {message.text}")