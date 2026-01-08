import os
import asyncio
from datetime import datetime

from .. import logger
from ..constants import STATISTIC_CALL_WAIT
from .config import ConfigLoader
from .stats import WatchdogStats

from ..parsing import (
    TotalParsers,
    BitcoinParsers,
    EthParsers,
    SignalParser,
)

from ..api.sender import ApiSender
from ..telegram.service import TelegramService
from ..console.interactive import InteractiveConsole

# TODO: __init__.py files

class TelegramWatchdog:

    def __init__(self, config_path: str = "watchdog_config.json"):
        self.config_path = config_path
        self.config = ConfigLoader(config_path).load()

        self.stats = WatchdogStats()

        self.channel_to_bot_mapping = {
            'TOTAL': 'ТОТАЛ_Бот',
            'BITCOIN': 'БИТКОИН_Бот',
            'ETH': 'ЭФИР_Бот'
        }

        self.api_url = os.getenv(
            "API_ENDPOINT",
            self.config.get('api_endpoint', 'http://localhost:8000/api/signals')
        )
        self.api_key = os.getenv(
            "API_KEY",
            self.config.get('api_key', '')
        )

        total = TotalParsers(self.channel_to_bot_mapping)
        btc = BitcoinParsers(self.channel_to_bot_mapping)
        eth = EthParsers(self.channel_to_bot_mapping)

        self.parser = SignalParser(
            self.config,
            self.channel_to_bot_mapping,
            total,
            btc,
            eth
        )

        self.api = ApiSender(
            self.api_url,
            self.api_key,
            self.config,
            self.stats
        )

        self.telegram = TelegramService(
            self.config,
            self.process_message
        )

        self.console = InteractiveConsole(self)

    async def process_message(self, event, group_type: str):
        try:
            message = event.message
            channel = await message.get_chat()
            channel_name = channel.username if channel.username else channel.title

            logger.debug(
                f"Сообщение из {channel_name} ({group_type}): "
                f"{message.text[:50]}..."
            )

            signal = await self.parser.parse_signal(
                message.text,
                channel_name,
                group_type
            )

            if signal:
                self.stats.signals_processed += 1
                self.stats.last_processed = datetime.now()

                success = await self.api.send(signal)

                if success:
                    if self.config.get('send_confirmation', False):
                        await message.reply(
                            f"✅ Сигнал обработан: "
                            f"{signal['action']} {signal['symbol']} "
                            f"(сила: {signal.get('strength', 1)}/3)"
                        )
                else:
                    logger.error(f"Не удалось отправить сигнал: {signal}")

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            self.stats.errors += 1

    async def print_stats(self):
        while True:
            await asyncio.sleep(STATISTIC_CALL_WAIT)

            logger.info(
                "\n📊 Статистика Watchdog:\n"
                f"Обработано сигналов: {self.stats.signals_processed}\n"
                f"Успешно отправлено: {self.stats.signals_sent}\n"
                f"Ошибок: {self.stats.errors}\n"
                f"Последний сигнал: "
                f"{self.stats.last_processed or 'Нет'}\n"
            )

    def reload_config(self):
        self.config = ConfigLoader(self.config_path).load()
        logger.info("Конфигурация перезагружена")

    async def start(self):
        logger.info("Запуск Telegram Watchdog...")

        await self.telegram.start()

        stats_task = asyncio.create_task(self.print_stats())
        console_task = asyncio.create_task(self.console.run())

        logger.info("✅ Watchdog запущен и готов к работе!")
        logger.info(
            f"Мониторим группы: "
            f"{', '.join(self.config['channels'].keys())}"
        )

        await asyncio.gather(stats_task, console_task)
