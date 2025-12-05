"""
ORM модель пользователя.
Таблица users хранит данные зарегистрированных пользователей.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    """
    Модель пользователя системы CloudMeet.
    
    Атрибуты:
        id: Уникальный идентификатор пользователя
        email: Email адрес (уникальный)
        hashed_password: Хеш пароля
        display_name: Отображаемое имя пользователя
        is_active: Флаг активности аккаунта
        created_at: Дата и время создания аккаунта
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, display_name={self.display_name})>"
