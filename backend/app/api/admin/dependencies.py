"""
Зависимости для админ-панели
"""

from fastapi import HTTPException, Request, status
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def verify_admin_key(request: Request):
    """
    Проверка административного ключа.
    В production используйте более надежную аутентификацию!
    """
    admin_key = request.headers.get("X-Admin-Key")
    
    # Простая проверка (в production вынесите в настройки)
    valid_keys = ["admin123", "super_secret_admin_key"]
    
    if not admin_key or admin_key not in valid_keys:
        # Для веб-интерфейса можно использовать query параметр
        admin_key = request.query_params.get("admin_key")
        if not admin_key or admin_key not in valid_keys:
            # Проверяем куки
            admin_key = request.cookies.get("admin_key")
            if not admin_key or admin_key not in valid_keys:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется административный доступ"
                )
    
    return {"is_admin": True}


def format_datetime(dt: Optional[datetime]) -> str:
    """Форматирование даты для отображения"""
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_price(price: float) -> str:
    """Форматирование цены"""
    if price >= 1000:
        return f"${price:,.0f}"
    elif price >= 1:
        return f"${price:,.2f}"
    else:
        return f"${price:.4f}"


def get_pagination_params(request: Request, default_per_page: int = 20):
    """Извлечение параметров пагинации из запроса"""
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", default_per_page))
    return page, per_page
