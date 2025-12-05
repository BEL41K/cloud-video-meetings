"""
Конфигурация приложения conference-service.
Все настройки загружаются из переменных окружения.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Название приложения
    APP_NAME: str = "CloudMeet Conference Service"
    DEBUG: bool = False
    
    # База данных PostgreSQL
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "cloudmeet"
    POSTGRES_PASSWORD: str = "cloudmeet_secret"
    POSTGRES_DB: str = "cloudmeet_conference"
    
    # Redis для кэширования
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT настройки (для валидации токенов)
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Настройки кэширования
    CACHE_TTL_SECONDS: int = 300  # 5 минут
    
    @property
    def DATABASE_URL(self) -> str:
        """Формирование строки подключения к БД"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def REDIS_URL(self) -> str:
        """Формирование строки подключения к Redis"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        extra = "allow"


# Глобальный экземпляр настроек
settings = Settings()
