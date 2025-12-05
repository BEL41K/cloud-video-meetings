"""
API endpoints для аутентификации.
Включает регистрацию, логин и получение информации о текущем пользователе.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.api.deps import get_current_user

# Настройка логгера
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.
    
    Args:
        user_data: Данные для регистрации (email, display_name, password)
        db: Сессия базы данных
    
    Returns:
        Данные созданного пользователя
    
    Raises:
        HTTPException: Если email уже зарегистрирован
    """
    logger.info(f"Попытка регистрации пользователя: {user_data.email}")
    
    # Проверка существования пользователя
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Email уже зарегистрирован: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создание нового пользователя
    new_user = User(
        email=user_data.email,
        display_name=user_data.display_name,
        hashed_password=get_password_hash(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Пользователь успешно зарегистрирован: {new_user.id}")
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Аутентификация пользователя и выдача JWT токена.
    
    Args:
        credentials: Учетные данные (email, password)
        db: Сессия базы данных
    
    Returns:
        JWT токен доступа
    
    Raises:
        HTTPException: Если учетные данные неверны
    """
    logger.info(f"Попытка входа пользователя: {credentials.email}")
    
    # Поиск пользователя
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Неудачная попытка входа: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )
    
    # Создание токена
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id), 
            "email": user.email,
            "display_name": user.display_name
        },
        expires_delta=access_token_expires
    )
    
    logger.info(f"Успешный вход пользователя: {user.id}")
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Получение информации о текущем авторизованном пользователе.
    
    Args:
        current_user: Текущий пользователь (из JWT токена)
    
    Returns:
        Данные текущего пользователя
    """
    return current_user


@router.get("/validate")
def validate_token(current_user: User = Depends(get_current_user)):
    """
    Проверка валидности токена.
    Используется gateway для проверки авторизации.
    
    Returns:
        ID и email пользователя
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name
    }
