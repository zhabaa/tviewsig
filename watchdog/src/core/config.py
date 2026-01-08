import json
import os
import sys
from typing import Dict
from .. import logger


class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def load(self) -> Dict:
        if not os.path.exists(self.config_path):
            template = {
                "telegram_api_id": 123456,
                "telegram_api_hash": "ваш_api_hash",
                "api_endpoint": "http://localhost:8000/api/signals",
                "api_key": "ваш_api_ключ",
                "channels": {
                    "TOTAL": "название_группы_тотал",
                    "BITCOIN": "название_группы_биткоин",
                    "ETH": "название_группы_эфир"
                },
                "parse_rules": {
                    "skip_keywords": [
                        "pin", "закреп", "pinned", "admin",
                        "реклама", "#Report", "LongReport"
                    ],
                    "bot_names": {
                        "default": "Telegram_Watchdog",
                        "channel_mapping": {
                            "TOTAL": "ТОТАЛ_Бот",
                            "BITCOIN": "БИТКОИН_Бот",
                            "ETH": "ЭФИР_Бот"
                        }
                    }
                },
                "monitoring": {
                    "check_interval": 300,
                    "retry_attempts": 3,
                    "retry_delay": 5
                }
            }

            with open(self.config_path, 'w') as f:
                json.dump(template, f, indent=2)

            logger.warning(f"Создан шаблон конфигурации в {self.config_path}. Заполните его!")
            sys.exit(1)

        with open(self.config_path, 'r') as f:
            return json.load(f)
