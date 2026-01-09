from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

# Сигналы
class SignalCreate(BaseModel):
    bot_name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=50)
    action: ActionType
    price: float = Field(..., gt=0)
    comment: Optional[str] = Field(None, max_length=500)
    timestamp: Optional[datetime] = None

class SignalResponse(SignalCreate):
    id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Пользователи
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_premium: bool = False

class UserResponse(UserCreate):
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserWithAPIKey(UserResponse):
    api_key: str
