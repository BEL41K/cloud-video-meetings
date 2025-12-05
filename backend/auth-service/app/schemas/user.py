"""
Pydantic схемы для валидации данных пользователя.
Используются для входящих запросов и исходящих ответов.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    display_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """Схема для регистрации нового пользователя"""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Схема для входа в систему"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные, извлекаемые из токена"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class MessageResponse(BaseModel):
    """Схема для простых текстовых ответов"""
    message: str
