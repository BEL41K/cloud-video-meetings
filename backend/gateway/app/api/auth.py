"""
Gateway endpoints для аутентификации.
Проксирует запросы к auth-service.
"""

import logging
from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Dict, Any

from app.core.config import settings
from app.services.proxy import proxy_request
from app.api.deps import get_current_user, CurrentUser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


@router.post("/register")
async def register(request: Request) -> Dict[str, Any]:
    """Проксирование регистрации к auth-service"""
    body = await request.json()
    
    return await proxy_request(
        method="POST",
        url=f"{settings.AUTH_SERVICE_URL}/api/auth/register",
        json_data=body
    )


@router.post("/login")
async def login(request: Request) -> Dict[str, Any]:
    """Проксирование логина к auth-service"""
    body = await request.json()
    
    return await proxy_request(
        method="POST",
        url=f"{settings.AUTH_SERVICE_URL}/api/auth/login",
        json_data=body
    )


@router.get("/me")
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Проксирование получения текущего пользователя"""
    headers = {}
    if credentials:
        headers["Authorization"] = f"Bearer {credentials.credentials}"
    
    return await proxy_request(
        method="GET",
        url=f"{settings.AUTH_SERVICE_URL}/api/auth/me",
        headers=headers
    )
