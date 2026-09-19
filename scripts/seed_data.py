from bot.db import SessionLocal
from bot.models import User, Topic, Source, UserTopic

session = SessionLocal()

# Замените на ваш реальный telegram_chat_id — узнать его можно через @userinfobot в Telegram
YOUR_CHAT_ID = 123456789

user = session.query(User).filter_by(telegram_chat_id=YOUR_CHAT_ID).first()
if user is None:
    user = User(telegram_chat_id=YOUR_CHAT_ID)
    session.add(user)
    session.commit()

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
        "name": "Отечественный геймдев",
        "description": (
            "Новости РАЗРАБОТКИ видеоигр, касающиеся ИСКЛЮЧИТЕЛЬНО России: российские "
            "студии-разработчики, российские издатели, релизы и анонсы российских проектов. "
            "НЕ включать общие мировые новости индустрии на русском языке — только те, где "
            "явно фигурирует российская студия/компания/проект. Если источник в основном "
            "пишет о зарубежных играх — такие статьи отфильтровывать."
        ),
        "depth_level": "briefly",
        "sources": [
            "https://app2top.ru/feed/",
            "http://www.playground.ru/rss/news.xml",
            "https://www.igromania.ru/rss/news.xml",
        ],
    },
    {
        "name": "Налогообложение РФ",
        "description": (
            "Изменения законов и поправок по налогам, касающиеся ТОЛЬКО физических лиц "
            "(не организаций и не ИП): НДФЛ, налог на имущество физлиц, налоговые вычеты, "
            "ЖКХ, недвижимость — применительно к гражданам РФ, значимо для Москвы и "
            "Московской области. Важно знать дату вступления в силу. Изменения, касающиеся "
            "исключительно юридических лиц (налог на прибыль организаций, НДС для бизнеса "
            "и т.п.), в дайджест не включать."
        ),
        "depth_level": "summary",
        "sources": [
            "https://www.consultant.ru/rss/db.xml",
            "https://www.consultant.ru/rss/hotdocs.xml",
        ],
    },
]

for data in topics_data:
    topic = session.query(Topic).filter_by(name=data["name"]).first()
    if topic is None:
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
    else:
        print(f"Тема уже существует, пропущена: {data['name']}")

session.close()
print("Готово.")
