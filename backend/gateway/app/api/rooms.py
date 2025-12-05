"""
Gateway endpoints для управления комнатами.
Проксирует запросы к conference-service.
"""

import logging
from fastapi import APIRouter, Depends, Request, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Dict, Any, Optional

from app.core.config import settings
from app.services.proxy import proxy_request
from app.api.deps import get_current_user, CurrentUser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rooms", tags=["rooms"])
security = HTTPBearer()


def get_auth_headers(credentials: HTTPAuthorizationCredentials) -> Dict[str, str]:
    """Формирование заголовков авторизации"""
    return {"Authorization": f"Bearer {credentials.credentials}"}


@router.post("")
async def create_room(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Создание комнаты"""
    body = await request.json()
    
    return await proxy_request(
        method="POST",
        url=f"{settings.CONFERENCE_SERVICE_URL}/api/rooms",
        headers=get_auth_headers(credentials),
        json_data=body
    )


@router.get("")
async def get_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    only_active: bool = Query(True),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Any:
    """Получение списка комнат"""
    return await proxy_request(
        method="GET",
        url=f"{settings.CONFERENCE_SERVICE_URL}/api/rooms",
        headers=get_auth_headers(credentials),
        params={"skip": skip, "limit": limit, "only_active": only_active}
    )


@router.get("/{room_id}")
async def get_room(
    room_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Получение информации о комнате"""
    return await proxy_request(
        method="GET",
        url=f"{settings.CONFERENCE_SERVICE_URL}/api/rooms/{room_id}",
        headers=get_auth_headers(credentials)
    )


@router.post("/{room_id}/join")
async def join_room(
    room_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Присоединение к комнате"""
    return await proxy_request(
        method="POST",
        url=f"{settings.CONFERENCE_SERVICE_URL}/api/rooms/{room_id}/join",
        headers=get_auth_headers(credentials)
    )


@router.post("/{room_id}/leave")
async def leave_room(
    room_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Выход из комнаты"""
    return await proxy_request(
        method="POST",
        url=f"{settings.CONFERENCE_SERVICE_URL}/api/rooms/{room_id}/leave",
        headers=get_auth_headers(credentials)
    )


@router.delete("/{room_id}")
async def delete_room(
    room_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Удаление комнаты"""
    return await proxy_request(
        method="DELETE",
        url=f"{settings.CONFERENCE_SERVICE_URL}/api/rooms/{room_id}",
        headers=get_auth_headers(credentials)
    )


@router.post("/{room_id}/messages")
async def send_message(
    room_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Отправка сообщения в чат"""
    body = await request.json()
    
    return await proxy_request(
        method="POST",
        url=f"{settings.CONFERENCE_SERVICE_URL}/api/rooms/{room_id}/messages",
        headers=get_auth_headers(credentials),
        json_data=body
    )


@router.get("/{room_id}/messages")
async def get_messages(
    room_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Получение сообщений чата"""
    return await proxy_request(
        method="GET",
        url=f"{settings.CONFERENCE_SERVICE_URL}/api/rooms/{room_id}/messages",
        headers=get_auth_headers(credentials),
        params={"skip": skip, "limit": limit}
    )
