from fastapi import APIRouter, HTTPException, status, Header
from passlib.context import CryptContext
import secrets
import logging
from app.core.database import db
from app.models.schemas import UserCreate, UserResponse, UserWithAPIKey
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# Для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=UserWithAPIKey, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    admin_key: str = Header(..., alias="X-Admin-Key")
):
    """Создать пользователя (требуется admin key)"""
    # Простая проверка admin key
    if admin_key != "admin123":
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    client = db.get_client()
    
    try:
        # Генерируем API ключ
        api_key = secrets.token_urlsafe(32)
        api_key_hash = pwd_context.hash(api_key)
        
        # Вставляем пользователя
        client.command("""
            INSERT INTO users (username, api_key_hash, full_name, is_premium)
            VALUES (%(username)s, %(api_key_hash)s, %(full_name)s, %(is_premium)s)
        """, {
            "username": user_data.username,
            "api_key_hash": api_key_hash,
            "full_name": user_data.full_name,
            "is_premium": user_data.is_premium
        })
        
        # Получаем созданного пользователя
        result = client.query("""
            SELECT username, full_name, is_premium, created_at
            FROM users WHERE username = %(username)s
        """, {"username": user_data.username})
        
        row = result.result_rows[0]
        return UserWithAPIKey(
            username=row[0],
            full_name=row[1],
            is_premium=row[2],
            created_at=row[3],
            api_key=api_key
        )
        
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=400, detail=f"User '{user_data.username}' already exists")
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """Получить информацию о текущем пользователе"""
    # Для MVP просто возвращаем заглушку
    return UserResponse(
        username="demo_user",
        full_name="Demo User",
        is_premium=False,
        created_at=datetime.utcnow()
    )
