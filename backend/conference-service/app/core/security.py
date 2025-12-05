"""
Модуль безопасности - декодирование JWT токенов.
"""

from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings


def decode_token(token: str) -> Optional[dict]:
    """
    Декодирование JWT токена.
    
    Args:
        token: JWT токен
    
    Returns:
        Декодированные данные или None при ошибке
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
