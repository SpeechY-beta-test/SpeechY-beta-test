import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from logger_config import app_logger


class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    EXP_FOR_IMPROVIZATION_TASKS: int
    DATABASE_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app_logger.info("Загрузка конфигурации Settings")
        app_logger.debug(f"Подключение к БД: {self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        url = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        print(f"URL для подключения: {url}")  # временно для отладки
        return url

    def get_bot_token(self):
        return self.BOT_TOKEN

    def get_EXP_FOR_IMPROVIZATION_TASKS(self):
        return self.EXP_FOR_IMPROVIZATION_TASKS


settings = Settings()
