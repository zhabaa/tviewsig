import clickhouse_connect

from core.logger import get_logger
from core.config import settings

logger = get_logger(__name__)


class Database:
    def __init__(self):
        self.client = None

    def connect(self):
        """Подключиться к ClickHouse"""
        try:
            self.client = clickhouse_connect.get_client(
                host=settings.CLICKHOUSE_HOST,
                port=settings.CLICKHOUSE_HTTP_PORT,
                username=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD,
            )

            self.client.command("CREATE DATABASE IF NOT EXISTS tv_signals")
            self.client.close()

            self.client = clickhouse_connect.get_client(
                host=settings.CLICKHOUSE_HOST,
                port=settings.CLICKHOUSE_HTTP_PORT,
                username=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD,
                database=settings.CLICKHOUSE_DB,
            )

            self._init_tables()
            logger.info("Connected to ClickHouse, database created")

        except Exception as e:
            logger.error(f"ClickHouse connection error: {e}")
            raise

    def _init_tables(self):
        """Создать таблицы если их нет"""

        self.client.command(
            """
            CREATE TABLE IF NOT EXISTS signals (
                id UUID DEFAULT generateUUIDv4(),
                bot_name String,
                symbol String,
                action String,
                price Float64,
                timestamp DateTime DEFAULT now(),
                comment Nullable(String)
            ) ENGINE = MergeTree()
            ORDER BY (timestamp, bot_name)
            """
        )

        # Пользователей
        self.client.command(
            """
            CREATE TABLE IF NOT EXISTS users (
                username String,
                api_key_hash String,
                full_name Nullable(String),
                is_premium Boolean DEFAULT false,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY username
            """
        )
        logger.info("Tables initialized")

    def get_client(self):
        """Получить клиент БД"""
        if not self.client:
            self.connect()

        return self.client


db = Database()
