TelegramBot NewsMyMind - Персональный новостной дайджест по заданным темам — коротко и по существу, каждый день в одно и то же время.   
# NewsMyMind — Telegram-бот для агрегации новостей

Бот собирает новости по заданным темам из RSS-источников, обрабатывает их с помощью ИИ (фильтрация по релевантности, устранение дублей, форматирование по уровню глубины) и присылает готовый дайджест в Telegram по расписанию.

Подробности о требованиях и архитектуре — см. `REQUIREMENTS.md` и `ARCHITECTURE.md`.

## Стек технологий

- Python 3.12, `aiogram` 3.x — Telegram-бот
- `feedparser` + `requests` — сбор новостей из RSS
- `SQLAlchemy` + `Alembic` — база данных (SQLite) и миграции
- `APScheduler` — планировщик рассылки
- Anthropic API — фильтрация, сопоставление и форматирование новостей (через собственную абстракцию `LLMProvider`, допускающую замену на другого провайдера, включая локальную модель)
- `pytest` — автоматические тесты
- Docker — упаковка и деплой

## Локальный запуск

1. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv venv
   venv\Scripts\Activate.ps1   # Windows
   pip install -r requirements.txt
   ```

2. Создайте файл `.env` в корне проекта (по образцу `.env.example`):
   ```
   BOT_TOKEN=токен_от_BotFather
   ANTHROPIC_API_KEY=ключ_Anthropic
   DB_PATH=news_bot.db
   ```
   **Никогда не коммитьте этот файл** — он уже в `.gitignore`.

3. Примените миграции (создаст файл БД со всеми таблицами):
   ```bash
   alembic upgrade head
   ```

4. Заполните базу данных вашими темами и источниками (отредактируйте `YOUR_CHAT_ID` в файле под свой Telegram ID, узнать через @userinfobot):
   ```bash
   python scripts/seed_data.py
   ```

5. Запустите бота:
   ```bash
   python main.py
   ```

## Тесты

```bash
pytest
```

Тесты покрывают: дедупликацию статей (`tests/test_db.py`), формирование промптов для ИИ и разбиение длинных сообщений (`tests/test_ai_processor.py`, `tests/test_digest_builder.py`), устойчивость сбора новостей к сетевым сбоям и битым данным (`tests/test_news_fetcher.py`). Внешние сервисы (Anthropic API, сеть) не вызываются реально — используются моки и заглушки (`llm_providers/fake_provider.py`, `unittest.mock`).

## Запуск через Docker (локально)

```bash
docker build -t news-bot .
docker run -d --name news-bot --env-file .env -v news-bot-data:/app/data --restart unless-stopped news-bot
docker logs -f news-bot
```

`-v news-bot-data:/app/data` — данные (файл БД) сохраняются в отдельном Docker volume и не теряются при пересоздании контейнера. Путь к БД внутри контейнера должен совпадать с тем, что указан в `DB_PATH` в `.env` (например, `/app/data/news_bot.db`).

## Деплой на сервер (VPS)

Текущий прод: FirstVDS, тариф VDS Старт, локация Амстердам (обоснование выбора локации — см. `REQUIREMENTS.md`, раздел 6).

1. Подключитесь по SSH:
   ```bash
   ssh root@IP_СЕРВЕРА
   ```

2. Установите Docker (один раз, при первой настройке сервера):
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

3. Склонируйте репозиторий и создайте `.env` (см. раздел "Локальный запуск", пункт 2 — на сервере `.env` создаётся так же, вручную, через `nano .env`, так как в Git он не попадает):
   ```bash
   git clone https://github.com/TerminalS16/news-bot.git
   cd news-bot
   nano .env
   ```

4. Соберите образ и запустите контейнер:
   ```bash
   docker build -t news-bot .
   docker run -d --name news-bot --env-file .env -v news-bot-data:/app/data --restart unless-stopped news-bot
   ```

5. При первом запуске на новом сервере заполните БД:
   ```bash
   docker exec -it news-bot python scripts/seed_data.py
   ```

### Обновление кода на сервере после изменений

```bash
cd ~/news-bot
git pull
docker stop news-bot
docker rm news-bot
docker build -t news-bot .
docker run -d --name news-bot --env-file .env -v news-bot-data:/app/data --restart unless-stopped news-bot
```

## Бэкап базы данных

Настроен автоматический ежедневный бэкап через cron (каждый день в 02:00 по времени сервера), с хранением копий за последние 7 дней. Скрипт — `/root/backup-db.sh` на сервере (не в репозитории, так как специфичен для конкретного сервера). Использует встроенный механизм `sqlite3.Connection.backup()` для безопасного копирования "на живую", без риска повреждения БД.

Проверить последние бэкапы на сервере:
```bash
ls -la /root/backups
cat /root/backup.log
```

## Полезные команды на сервере

```bash
docker ps                    # проверить, что контейнер запущен
docker logs -f news-bot      # логи в реальном времени
docker restart news-bot      # перезапустить бота
docker exec -it news-bot bash  # зайти внутрь контейнера
```
