import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from bot.db import SessionLocal
from bot.models import User, Topic, Source, UserTopic

session = SessionLocal()

YOUR_CHAT_ID = 813991567  # ваш реальный ID, уже известный из ошибки

user = session.scalar(select(User).where(User.telegram_chat_id == YOUR_CHAT_ID))
if user is None:
    user = User(telegram_chat_id=YOUR_CHAT_ID)
    session.add(user)
    session.commit()
    print("Создан новый пользователь.")
else:
    print("Пользователь уже существует, используем существующего.")

topics_data = [
    {
        "name": "BTS",
        "description": "Новости исключительно о группе BTS и её участниках: анонсы концертов, новые песни и проекты. Без подробностей личной жизни и быта.",
        "depth_level": "briefly",
        "sources": [
            "https://www.soompi.com/feed",
            "https://en.yna.co.kr/RSS/news.xml",
        ],
    },
    {
        "name": "Видеоигры",
        "description": "Только самые громкие и важные события индустрии видеоигр (крупные анонсы, релизы новых консолей и игр), без деталей.",
        "depth_level": "briefly",
        "sources": [
            "https://www.goha.ru/rss/videogames",
            "https://www.ign.com/rss/articles/feed",
            "https://www.polygon.com/feed/",
            "https://www.gamespot.com/feeds/mashup/",
        ],
    },
    {
        "name": "Налогообложение РФ",
        "description": "Изменения законов и поправок по налогам для граждан РФ, значимых для Москвы и Московской области: ЖКХ, недвижимость, НДС и т.п. Важно знать дату вступления в силу.",
        "depth_level": "summary",
        "sources": [
            "https://www.consultant.ru/rss/db.xml",
            "https://www.consultant.ru/rss/hotdocs.xml",
        ],
    },
]

for data in topics_data:
    topic = Topic(name=data["name"], description=data["description"])
    session.add(topic)
    session.commit()

    for source_url in data["sources"]:
        source = Source(topic_id=topic.id, type="rss", url_or_query=source_url, is_active=True)
        session.add(source)
    session.commit()

    user_topic = UserTopic(
        user_id=user.id,
        topic_id=topic.id,
        depth_level=data["depth_level"],
        is_active=True,
    )
    session.add(user_topic)
    session.commit()

    print(f"Добавлена тема: {data['name']} ({len(data['sources'])} источник(ов))")

session.close()
print("Готово.")