"""
ORM модель участника комнаты.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class ParticipantStatus(str, enum.Enum):
    """Статус участника в комнате"""
    ONLINE = "online"
    IN_CALL = "in_call"
    OFFLINE = "offline"


class RoomParticipant(Base):
    """
    Модель участника комнаты видеоконференции.
    
    Атрибуты:
        id: Уникальный идентификатор записи
        room_id: ID комнаты
        user_id: ID пользователя
        user_display_name: Отображаемое имя пользователя
        status: Статус участника (online, in_call, offline)
        join_time: Время присоединения к комнате
        leave_time: Время выхода из комнаты
    """
    
    __tablename__ = "room_participants"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_display_name = Column(String(100), nullable=False)
    status = Column(String(20), default=ParticipantStatus.ONLINE.value)
    join_time = Column(DateTime(timezone=True), server_default=func.now())
    leave_time = Column(DateTime(timezone=True), nullable=True)
    
    # Связь с комнатой
    room = relationship("Room", back_populates="participants")
    
    def __repr__(self):
        return f"<RoomParticipant(room_id={self.room_id}, user_id={self.user_id}, status={self.status})>"
