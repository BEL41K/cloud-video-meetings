"""
Зависимости для API endpoints.
Включает функции для извлечения данных текущего пользователя из токена.
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.core.security import decode_token
from pydantic import BaseModel

# Схема Bearer токена
security = HTTPBearer()


class CurrentUser(BaseModel):
    """Данные текущего пользователя из токена"""
    user_id: int
    email: str
    display_name: Optional[str] = None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Получение данных текущего пользователя из JWT токена.
    
    Raises:
        HTTPException: Если токен недействителен
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    email = payload.get("email")
    display_name = payload.get("display_name") or email
    
    if user_id is None:
        raise credentials_exception
    
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception
    
    return CurrentUser(
        user_id=user_id_int,
        email=email,
        display_name=display_name
    )


def get_current_user_from_header(
    x_user_id: int = Header(..., alias="X-User-ID"),
    x_user_email: str = Header(..., alias="X-User-Email"),
    x_user_name: str = Header(None, alias="X-User-Name")
) -> CurrentUser:
    """
    Получение данных пользователя из заголовков запроса.
    Используется когда gateway передает данные пользователя.
    """
    return CurrentUser(
        user_id=x_user_id,
        email=x_user_email,
        display_name=x_user_name or x_user_email
    )
