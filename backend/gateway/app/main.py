"""
Точка входа API Gateway.
Единый публичный API для платформы CloudMeet Lite.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.rooms import router as rooms_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом Gateway"""
    logger.info("Запуск API Gateway...")
    logger.info(f"Auth Service URL: {settings.AUTH_SERVICE_URL}")
    logger.info(f"Conference Service URL: {settings.CONFERENCE_SERVICE_URL}")
    yield
    logger.info("Остановка API Gateway...")


# Создание FastAPI приложения
app = FastAPI(
    title=settings.APP_NAME,
    description="API Gateway для платформы CloudMeet Lite",
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
app.include_router(auth_router)
app.include_router(rooms_router)


@app.get("/health")
def health_check():
    """Проверка состояния Gateway"""
    return {"status": "healthy", "service": "gateway"}


@app.get("/")
def root():
    """Корневой endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth",
            "rooms": "/api/rooms"
        }
    }
