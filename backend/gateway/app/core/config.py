"""
Конфигурация API Gateway.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Gateway"""
    
    APP_NAME: str = "CloudMeet API Gateway"
    DEBUG: bool = False
    
    # URL внутренних сервисов
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    CONFERENCE_SERVICE_URL: str = "http://conference-service:8000"
    
    # JWT настройки
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
