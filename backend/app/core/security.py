from passlib.context import CryptContext
import secrets
import logging
from fastapi import HTTPException, status, Header
from typing import Optional, Dict
from app.core.database import db

logger = logging.getLogger(__name__)

class Security:
    """Упрощенный сервис безопасности"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_api_key(self, api_key: str) -> str:
        """Хешировать API ключ"""
        return self.pwd_context.hash(api_key)
    
    def verify_api_key(self, plain_key: str, hashed_key: str) -> bool:
        """Проверить API ключ"""
        return self.pwd_context.verify(plain_key, hashed_key)
    
    def generate_api_key(self) -> str:
        """Сгенерировать API ключ"""
        return secrets.token_urlsafe(32)
    
    def authenticate(self, api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Dict:
        """Аутентифицировать пользователя"""
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        
        client = db.get_client()
        
        # Получаем всех пользователей
        result = client.query("SELECT username, api_key_hash, is_premium FROM users")
        
        for username, stored_hash, is_premium in result.result_rows:
            if self.verify_api_key(api_key, stored_hash):
                return {
                    "username": username,
                    "is_premium": is_premium
                }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )


security = Security()
