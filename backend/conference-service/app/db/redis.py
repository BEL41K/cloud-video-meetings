"""
Клиент Redis для кэширования данных.
"""

import json
import logging
from typing import Optional, Any
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Глобальный клиент Redis
redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Получение клиента Redis"""
    global redis_client
    
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            redis_client.ping()
            logger.info("Подключение к Redis установлено")
        except redis.ConnectionError as e:
            logger.error(f"Ошибка подключения к Redis: {e}")
            raise
    
    return redis_client


def cache_set(key: str, value: Any, ttl: int = None) -> bool:
    """
    Сохранение значения в кэш.
    
    Args:
        key: Ключ кэша
        value: Значение для сохранения
        ttl: Время жизни в секундах
    
    Returns:
        True если успешно, False при ошибке
    """
    try:
        client = get_redis_client()
        json_value = json.dumps(value, default=str)
        if ttl:
            client.setex(key, ttl, json_value)
        else:
            client.set(key, json_value)
        return True
    except Exception as e:
        logger.error(f"Ошибка записи в кэш: {e}")
        return False


def cache_get(key: str) -> Optional[Any]:
    """
    Получение значения из кэша.
    
    Args:
        key: Ключ кэша
    
    Returns:
        Значение из кэша или None
    """
    try:
        client = get_redis_client()
        value = client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Ошибка чтения из кэша: {e}")
        return None


def cache_delete(key: str) -> bool:
    """
    Удаление значения из кэша.
    
    Args:
        key: Ключ кэша
    
    Returns:
        True если успешно
    """
    try:
        client = get_redis_client()
        client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления из кэша: {e}")
        return False


def cache_delete_pattern(pattern: str) -> bool:
    """
    Удаление значений по паттерну ключа.
    
    Args:
        pattern: Паттерн ключей (например, "room:*")
    
    Returns:
        True если успешно
    """
    try:
        client = get_redis_client()
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления по паттерну: {e}")
        return False
