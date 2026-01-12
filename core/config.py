import os
from dotenv import load_dotenv, find_dotenv


class Settings:
    load_dotenv(find_dotenv())

    APP_NAME: str = "Crypto Signals API"
    APP_VERSION: str = "1.0.0"

    CLICKHOUSE_HOST: str = os.getenv("CLICKHOUSE_HOST", "")
    CLICKHOUSE_PORT: int = int(os.getenv("CLICKHOUSE_PORT", ""))
    CLICKHOUSE_HTTP_PORT: int = int(os.getenv("CLICKHOUSE_HTTP_PORT", ""))
    CLICKHOUSE_USER: str = os.getenv("CLICKHOUSE_USER", "")
    CLICKHOUSE_DB: str = os.getenv("CLICKHOUSE_DB", "")
    CLICKHOUSE_PASSWORD: str = os.getenv("CLICKHOUSE_PASSWORD", "")

    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    @classmethod
    def validate(cls):
        assert cls.CLICKHOUSE_HOST, "CLICKHOUSE_HOST is not set"
        assert cls.CLICKHOUSE_PORT, "CLICKHOUSE_PORT is not set"
        assert cls.CLICKHOUSE_USER, "CLICKHOUSE_USER is not set"
        assert cls.CLICKHOUSE_DB, "CLICKHOUSE_DB is not set"
        assert cls.CLICKHOUSE_PASSWORD, "CLICKHOUSE_PASSWORD is not set"


settings = Settings()

try:
    settings.validate()

except AssertionError as e:
    print(f"Configuration error: {e}") # Add logger TODO
