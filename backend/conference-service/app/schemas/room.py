"""
Pydantic схемы для комнат видеоконференций.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class RoomBase(BaseModel):
    """Базовая схема комнаты"""
    name: str = Field(..., min_length=1, max_length=255, description="Название комнаты")


class RoomCreate(RoomBase):
    """Схема для создания комнаты"""
    pass


class RoomResponse(RoomBase):
    """Схема ответа с данными комнаты"""
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    participants_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class RoomDetail(RoomResponse):
    """Детальная информация о комнате с участниками"""
    participants: List["ParticipantResponse"] = []
    
    class Config:
        from_attributes = True


class ParticipantResponse(BaseModel):
    """Схема ответа с данными участника"""
    id: int
    user_id: int
    user_display_name: str
    status: str
    is_owner: bool = False
    join_time: datetime
    leave_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JoinRoomRequest(BaseModel):
    """Схема запроса на присоединение к комнате"""
    pass


class JoinRoomResponse(BaseModel):
    """Схема ответа на присоединение к комнате"""
    message: str
    participant_id: int
    room_id: int


class LeaveRoomResponse(BaseModel):
    """Схема ответа на выход из комнаты"""
    message: str


# Обновляем forward reference
RoomDetail.model_rebuild()
