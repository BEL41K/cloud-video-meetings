"""
Зависимости для API Gateway.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel
from app.core.security import decode_token

security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """Данные текущего пользователя"""
    user_id: int
    email: str
    display_name: Optional[str] = None


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[CurrentUser]:
    """
    Опциональное получение текущего пользователя.
    Не выбрасывает ошибку, если токен отсутствует.
    """
    if credentials is None:
        return None
    
    payload = decode_token(credentials.credentials)
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if user_id is None:
        return None
    
    return CurrentUser(
        user_id=user_id,
        email=email,
        display_name=email
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Получение текущего пользователя.
    Выбрасывает ошибку, если токен недействителен.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if credentials is None:
        raise credentials_exception
    
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if user_id is None:
        raise credentials_exception
    
    return CurrentUser(
        user_id=user_id,
        email=email,
        display_name=email
    )
