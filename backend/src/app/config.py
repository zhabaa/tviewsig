import os
from typing import Optional

class Settings:
    # ClickHouse
    CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
    CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
    CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "TupayaFrigitnaya12312")
    CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "tv_signals")
    
    # App
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    APP_NAME = "Crypto Signals API"
    APP_VERSION = "1.0.0"

settings = Settings()
