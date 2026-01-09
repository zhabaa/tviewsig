from fastapi import FastAPI
import logging
from app.api.endpoints import signals, users
from app.config import settings
from app.core.database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
def startup():
    """Инициализация при запуске"""
    try:
        # Подключаемся к БД
        db.connect()
        logger.info("Database connected")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")

# Роутеры
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Health check
@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "status": "running"}

@app.get("/health")
async def health():
    try:
        client = db.get_client()
        client.command("SELECT 1")
        return {
            "status": "healthy", 
            "database": "connected",
            "tables": {
                "signals": True,
                "users": True
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
