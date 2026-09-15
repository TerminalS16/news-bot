from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    anthropic_api_key: str
    db_path: str = "news_bot.db"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()