"""
ORM модель сообщения чата в комнате.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Message(Base):
    """
    Модель сообщения чата в комнате видеоконференции.
    
    Атрибуты:
        id: Уникальный идентификатор сообщения
        room_id: ID комнаты
        user_id: ID отправителя
        user_display_name: Отображаемое имя отправителя
        content: Текст сообщения
        created_at: Время отправки сообщения
    """
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_display_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь с комнатой
    room = relationship("Room", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, room_id={self.room_id}, user_id={self.user_id})>"
