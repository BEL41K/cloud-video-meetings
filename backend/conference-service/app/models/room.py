"""
ORM модель комнаты видеоконференции.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Room(Base):
    """
    Модель комнаты видеоконференции.
    
    Атрибуты:
        id: Уникальный идентификатор комнаты
        name: Название комнаты
        owner_id: ID создателя комнаты
        is_active: Флаг активности комнаты
        created_at: Дата и время создания
    """
    
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    participants = relationship("RoomParticipant", back_populates="room", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Room(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
