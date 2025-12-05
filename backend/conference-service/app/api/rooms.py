"""
API endpoints для управления комнатами видеоконференций.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.redis import cache_get, cache_set, cache_delete, cache_delete_pattern
from app.models.room import Room
from app.models.participant import RoomParticipant, ParticipantStatus
from app.schemas.room import (
    RoomCreate, RoomResponse, RoomDetail, 
    JoinRoomResponse, LeaveRoomResponse, ParticipantResponse
)
from app.api.deps import get_current_user, CurrentUser
from app.core.config import settings

# Настройка логгера
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Создание новой комнаты видеоконференции.
    
    Args:
        room_data: Данные для создания комнаты
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Данные созданной комнаты
    """
    logger.info(f"Создание комнаты '{room_data.name}' пользователем {current_user.user_id}")
    
    new_room = Room(
        name=room_data.name,
        owner_id=current_user.user_id,
        is_active=True
    )
    
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    
    # Инвалидация кэша списка комнат
    cache_delete_pattern("rooms:*")
    
    logger.info(f"Комната создана: ID={new_room.id}")
    
    return RoomResponse(
        id=new_room.id,
        name=new_room.name,
        owner_id=new_room.owner_id,
        is_active=new_room.is_active,
        created_at=new_room.created_at,
        participants_count=0
    )


@router.get("", response_model=List[RoomResponse])
def get_rooms(
    skip: int = Query(0, ge=0, description="Пропустить записей"),
    limit: int = Query(20, ge=1, le=100, description="Количество записей"),
    only_active: bool = Query(True, description="Только активные комнаты"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Получение списка комнат с пагинацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей
        only_active: Фильтр по активным комнатам
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Список комнат
    """
    cache_key = f"rooms:list:{skip}:{limit}:{only_active}"
    
    # Проверка кэша
    cached_rooms = cache_get(cache_key)
    if cached_rooms:
        logger.debug("Список комнат получен из кэша")
        return [RoomResponse(**room) for room in cached_rooms]
    
    # Запрос к БД
    query = db.query(Room)
    
    if only_active:
        query = query.filter(Room.is_active == True)
    
    rooms = query.order_by(Room.created_at.desc()).offset(skip).limit(limit).all()
    
    # Формирование ответа с подсчетом участников
    result = []
    for room in rooms:
        participants_count = db.query(func.count(RoomParticipant.id)).filter(
            RoomParticipant.room_id == room.id,
            RoomParticipant.status != ParticipantStatus.OFFLINE.value
        ).scalar()
        
        result.append(RoomResponse(
            id=room.id,
            name=room.name,
            owner_id=room.owner_id,
            is_active=room.is_active,
            created_at=room.created_at,
            participants_count=participants_count
        ))
    
    # Сохранение в кэш
    cache_set(cache_key, [r.model_dump() for r in result], ttl=settings.CACHE_TTL_SECONDS)
    
    return result


@router.get("/{room_id}", response_model=RoomDetail)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Получение детальной информации о комнате.
    
    Args:
        room_id: ID комнаты
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Детальная информация о комнате с участниками
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комната не найдена"
        )
    
    # Получение активных участников
    participants = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.status != ParticipantStatus.OFFLINE.value
    ).all()
    
    return RoomDetail(
        id=room.id,
        name=room.name,
        owner_id=room.owner_id,
        is_active=room.is_active,
        created_at=room.created_at,
        participants_count=len(participants),
        participants=[ParticipantResponse(
            id=p.id,
            user_id=p.user_id,
            user_display_name=p.user_display_name,
            status=p.status,
            is_owner=(p.user_id == room.owner_id),
            join_time=p.join_time,
            leave_time=p.leave_time
        ) for p in participants]
    )


@router.post("/{room_id}/join", response_model=JoinRoomResponse)
def join_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Присоединение к комнате видеоконференции.
    
    Args:
        room_id: ID комнаты
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Информация о присоединении
    """
    logger.info(f"Пользователь {current_user.user_id} присоединяется к комнате {room_id}")
    
    # Проверка существования комнаты
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комната не найдена или неактивна"
        )
    
    # Проверка, не присоединен ли уже пользователь
    existing_participant = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == current_user.user_id,
        RoomParticipant.status != ParticipantStatus.OFFLINE.value
    ).first()
    
    if existing_participant:
        # Обновляем статус на in_call
        existing_participant.status = ParticipantStatus.IN_CALL.value
        db.commit()
        
        return JoinRoomResponse(
            message="Вы уже в комнате",
            participant_id=existing_participant.id,
            room_id=room_id
        )
    
    # Создание записи участника
    participant = RoomParticipant(
        room_id=room_id,
        user_id=current_user.user_id,
        user_display_name=current_user.display_name or current_user.email,
        status=ParticipantStatus.IN_CALL.value
    )
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    
    # Инвалидация кэша
    cache_delete_pattern(f"rooms:*")
    
    logger.info(f"Пользователь {current_user.user_id} присоединился к комнате {room_id}")
    
    return JoinRoomResponse(
        message="Вы успешно присоединились к комнате",
        participant_id=participant.id,
        room_id=room_id
    )


@router.post("/{room_id}/leave", response_model=LeaveRoomResponse)
def leave_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Выход из комнаты видеоконференции.
    
    Args:
        room_id: ID комнаты
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Подтверждение выхода
    """
    logger.info(f"Пользователь {current_user.user_id} выходит из комнаты {room_id}")
    
    # Поиск участника
    participant = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == current_user.user_id,
        RoomParticipant.status != ParticipantStatus.OFFLINE.value
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы не находитесь в этой комнате"
        )
    
    # Обновление статуса
    from datetime import datetime
    participant.status = ParticipantStatus.OFFLINE.value
    participant.leave_time = datetime.utcnow()
    db.commit()
    
    # Инвалидация кэша
    cache_delete_pattern(f"rooms:*")
    
    logger.info(f"Пользователь {current_user.user_id} вышел из комнаты {room_id}")
    
    return LeaveRoomResponse(message="Вы вышли из комнаты")


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Удаление комнаты (деактивация).
    Только владелец может удалить комнату.
    
    Args:
        room_id: ID комнаты
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комната не найдена"
        )
    
    if room.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только владелец может удалить комнату"
        )
    
    room.is_active = False
    db.commit()
    
    # Инвалидация кэша
    cache_delete_pattern(f"rooms:*")
    
    logger.info(f"Комната {room_id} деактивирована пользователем {current_user.user_id}")
