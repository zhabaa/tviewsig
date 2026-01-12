import logging
import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.admin.routes import router as admin_router
from app.api.endpoints import signals, users
from core.config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем директории если их нет
Path("src/app/api/admin/static").mkdir(exist_ok=True, parents=True)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Монтируем статические файлы для админки
app.mount(
    "/admin/static",
    StaticFiles(directory="src/app/api/admin/static"),
    name="admin_static",
)

# Настройка шаблонов для админки
templates = Jinja2Templates(directory="src/app/api/admin/templates")

# Подключаем роутеры

# Основное API
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Админ-панель
app.include_router(admin_router, prefix="/admin", tags=["admin"])


# Health check
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "endpoints": {
            "api_docs": "/docs",
            "admin_panel": "/admin",
            "api_signals": "/api/signals/",
            "api_users": "/api/users/",
        },
    }


@app.get("/health")
async def health():
    try:
        from app.core.database import db

        client = db.get_client()
        client.command("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
