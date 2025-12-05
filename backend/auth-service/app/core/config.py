"""
Конфигурация приложения auth-service.
Все настройки загружаются из переменных окружения.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Название приложения
    APP_NAME: str = "CloudMeet Auth Service"
    DEBUG: bool = False
    
    # База данных PostgreSQL
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "cloudmeet"
    POSTGRES_PASSWORD: str = "cloudmeet_secret"
    POSTGRES_DB: str = "cloudmeet_auth"
    
    # JWT настройки
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    @property
    def DATABASE_URL(self) -> str:
        """Формирование строки подключения к БД"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    class Config:
        env_file = ".env"
        extra = "allow"


# Глобальный экземпляр настроек
settings = Settings()
