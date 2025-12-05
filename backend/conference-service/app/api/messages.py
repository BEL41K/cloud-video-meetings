"""
API endpoints для сообщений чата в комнатах.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.redis import cache_get, cache_set, cache_delete, cache_delete_pattern
from app.models.room import Room
from app.models.participant import RoomParticipant, ParticipantStatus
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageResponse, MessagesListResponse
from app.api.deps import get_current_user, CurrentUser
from app.core.config import settings

# Настройка логгера
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(prefix="/api/rooms", tags=["messages"])


@router.post("/{room_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    room_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Отправка сообщения в чат комнаты.
    
    Args:
        room_id: ID комнаты
        message_data: Данные сообщения
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Данные отправленного сообщения
    """
    logger.info(f"Отправка сообщения в комнату {room_id} от пользователя {current_user.user_id}")
    
    # Проверка существования комнаты
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комната не найдена или неактивна"
        )
    
    # Проверка, что пользователь является участником комнаты
    participant = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == current_user.user_id,
        RoomParticipant.status != ParticipantStatus.OFFLINE.value
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь участником этой комнаты"
        )
    
    # Создание сообщения
    new_message = Message(
        room_id=room_id,
        user_id=current_user.user_id,
        user_display_name=current_user.display_name or current_user.email,
        content=message_data.content
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Инвалидация кэша сообщений (удаляем все ключи messages:{room_id}:*)
    cache_delete_pattern(f"messages:{room_id}:*")
    
    logger.info(f"Сообщение {new_message.id} отправлено в комнату {room_id}")
    
    return MessageResponse(
        id=new_message.id,
        room_id=new_message.room_id,
        user_id=new_message.user_id,
        user_display_name=new_message.user_display_name,
        is_owner=(new_message.user_id == room.owner_id),
        content=new_message.content,
        created_at=new_message.created_at
    )


@router.get("/{room_id}/messages", response_model=MessagesListResponse)
def get_messages(
    room_id: int,
    skip: int = Query(0, ge=0, description="Пропустить записей"),
    limit: int = Query(50, ge=1, le=200, description="Количество записей"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Получение истории сообщений комнаты.
    
    Args:
        room_id: ID комнаты
        skip: Количество записей для пропуска
        limit: Максимальное количество записей
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Список сообщений
    """
    # Проверка существования комнаты
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комната не найдена"
        )
    
    # Проверка кэша для последних сообщений
    cache_key = f"messages:{room_id}:{skip}:{limit}"
    cached_messages = cache_get(cache_key)
    
    if cached_messages:
        logger.debug(f"Сообщения комнаты {room_id} получены из кэша")
        return MessagesListResponse(
            messages=[MessageResponse(**msg) for msg in cached_messages["messages"]],
            total=cached_messages["total"]
        )
    
    # Подсчет общего количества сообщений
    total = db.query(func.count(Message.id)).filter(Message.room_id == room_id).scalar()
    
    # Получение сообщений
    messages = db.query(Message).filter(
        Message.room_id == room_id
    ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
    
    result = MessagesListResponse(
        messages=[MessageResponse(
            id=msg.id,
            room_id=msg.room_id,
            user_id=msg.user_id,
            user_display_name=msg.user_display_name,
            is_owner=(msg.user_id == room.owner_id),
            content=msg.content,
            created_at=msg.created_at
        ) for msg in messages],
        total=total
    )
    
    # Сохранение в кэш (очень короткий TTL для чата)
    cache_set(cache_key, {
        "messages": [m.model_dump() for m in result.messages],
        "total": total
    }, ttl=2)  # 2 секунды для чата
    
    return result
