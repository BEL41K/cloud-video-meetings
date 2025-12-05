"""
Pydantic схемы для сообщений чата.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class MessageBase(BaseModel):
    """Базовая схема сообщения"""
    content: str = Field(..., min_length=1, max_length=2000, description="Текст сообщения")


class MessageCreate(MessageBase):
    """Схема для создания сообщения"""
    pass


class MessageResponse(MessageBase):
    """Схема ответа с данными сообщения"""
    id: int
    room_id: int
    user_id: int
    user_display_name: str
    is_owner: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessagesListResponse(BaseModel):
    """Схема списка сообщений"""
    messages: List[MessageResponse]
    total: int
