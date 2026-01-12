import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.config import settings

PROJECT_ROOT = Path(__file__).parent.parent
FILE_CAPACITY = 1024 * 1024 * 5
FILES_AMOUNT = 3


def setup_logger(name: str = "app") -> logging.Logger:
    """Создает настроенный логгер"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        log_dir / f"{name}.log",
        maxBytes=FILE_CAPACITY,
        backupCount=FILES_AMOUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger("app")


def get_logger(module_name: str) -> logging.Logger:
    """Возвращает логгер для любого файла проекта"""
    return logging.getLogger(f"app.{module_name}")
