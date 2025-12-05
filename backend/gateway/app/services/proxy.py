"""
HTTP клиент для проксирования запросов к внутренним сервисам.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Таймаут для запросов
TIMEOUT = 30.0


async def proxy_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Проксирование HTTP запроса к внутреннему сервису.
    
    Args:
        method: HTTP метод (GET, POST, PUT, DELETE)
        url: Полный URL для запроса
        headers: Заголовки запроса
        json_data: JSON тело запроса
        params: Query параметры
    
    Returns:
        JSON ответ от сервиса
    
    Raises:
        HTTPException: При ошибке запроса
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params
            )
            
            # Если ответ с ошибкой от сервиса, пробрасываем её
            if response.status_code >= 400:
                try:
                    error_detail = response.json()
                except:
                    error_detail = {"detail": response.text}
                
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail.get("detail", "Ошибка сервиса")
                )
            
            # Для 204 No Content возвращаем пустой ответ
            if response.status_code == 204:
                return {}
            
            return response.json()
            
    except httpx.TimeoutException:
        logger.error(f"Таймаут запроса к {url}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Сервис не отвечает"
        )
    except httpx.ConnectError:
        logger.error(f"Ошибка подключения к {url}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис недоступен"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при запросе к {url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
