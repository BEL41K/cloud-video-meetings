"""
Точка входа приложения Conference Service.
FastAPI приложение для управления комнатами видеоконференций CloudMeet.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import create_tables
from app.api.rooms import router as rooms_router
from app.api.messages import router as messages_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    Создает таблицы БД и подключается к Redis при старте.
    """
    logger.info("Запуск Conference Service...")
    
    # Создание таблиц при старте
    try:
        create_tables()
        logger.info("Таблицы базы данных созданы/проверены")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
    
    # Проверка подключения к Redis
    try:
        from app.db.redis import get_redis_client
        get_redis_client()
        logger.info("Подключение к Redis установлено")
    except Exception as e:
        logger.warning(f"Redis недоступен, кэширование отключено: {e}")
    
    yield
    
    logger.info("Остановка Conference Service...")


# Создание FastAPI приложения
app = FastAPI(
    title=settings.APP_NAME,
    description="Сервис управления комнатами видеоконференций CloudMeet Lite",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(rooms_router)
app.include_router(messages_router)


@app.get("/health")
def health_check():
    """
    Проверка состояния сервиса.
    Используется для health checks в Docker/Kubernetes.
    """
    return {"status": "healthy", "service": "conference-service"}


@app.get("/")
def root():
    """Корневой endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }
