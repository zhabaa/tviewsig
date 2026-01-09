import logging
import sys
from logging.handlers import RotatingFileHandler
from app.config import settings


def setup_logging():
    """Настройка логирования для приложения"""

    # Формат логов
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Логи в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Логи в файл (с ротацией)
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10_485_760,  # 10MB
        backupCount=5,
    )
    file_handler.setFormatter(formatter)

    # Уровень логирования
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Настройка для конкретных логгеров
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(
        logging.DEBUG if settings.debug else logging.WARNING
    )

    # Убираем логи от сторонних библиотек если не нужно
    if not settings.debug:
        logging.getLogger("clickhouse_connect").setLevel(logging.WARNING)

    return root_logger
