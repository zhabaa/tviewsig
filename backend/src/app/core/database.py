import clickhouse_connect
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """Упрощенный синхронный клиент ClickHouse"""
    
    def __init__(self):
        self.client = None
    
    def connect(self):
        """Подключиться к ClickHouse"""
        try:
            # Сначала подключаемся без указания базы данных
            self.client = clickhouse_connect.get_client(
                host='clickhouse',
                port=8123,
                username='default',
                password='TupayaFrigitnaya12312'
                # Не указываем database тут
            )
            
            # Создаем базу данных если не существует
            self.client.command("CREATE DATABASE IF NOT EXISTS tv_signals")
            
            # Переподключаемся с указанием базы данных
            self.client.close()
            self.client = clickhouse_connect.get_client(
                host='clickhouse',
                port=8123,
                username='default',
                password='TupayaFrigitnaya12312',
                database='tv_signals'
            )
            
            self._init_tables()
            logger.info("Connected to ClickHouse, database created")
        except Exception as e:
            logger.error(f"ClickHouse connection error: {e}")
            raise
    
    def _init_tables(self):
        """Создать таблицы если их нет"""
        # Таблица сигналов
        self.client.command("""
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
        """)
        
        # Таблица пользователей
        self.client.command("""
            CREATE TABLE IF NOT EXISTS users (
                username String,
                api_key_hash String,
                full_name Nullable(String),
                is_premium Boolean DEFAULT false,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY username
        """)
        logger.info("Tables initialized")
    
    def get_client(self):
        """Получить клиент БД"""
        if not self.client:
            self.connect()
        return self.client

# Глобальный экземпляр
db = Database()
