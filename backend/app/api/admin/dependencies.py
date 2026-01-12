from datetime import datetime
from typing import Optional

from fastapi import HTTPException, Request, status

from core.logger import get_logger
from core.config import settings

logger = get_logger(__name__)



def verify_admin_key(request: Request):
    admin_key = request.headers.get("X-Admin-Key")

    # Простая проверка (в production вынесите в настройки)
    valid_keys = [settings.ADMINPANEL_PASSWORD]
    if not admin_key or admin_key not in valid_keys:
        # Для веб-интерфейса можно использовать query параметр
        admin_key = request.query_params.get("admin_key")
        if not admin_key or admin_key not in valid_keys:
            # Проверяем куки
            admin_key = request.cookies.get("admin_key")
            if not admin_key or admin_key not in valid_keys:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется административный доступ",
                )

    return {"is_admin": True}


def format_datetime(dt: Optional[datetime]) -> str:
    if not dt:
        return ""

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_price(price: float) -> str:
    if price >= 1000:
        return f"${price:,.0f}"

    elif price >= 1:
        return f"${price:,.2f}"

    else:
        return f"${price:.4f}"


def get_pagination_params(request: Request, default_per_page: int = 20):
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", default_per_page))
    return page, per_page
