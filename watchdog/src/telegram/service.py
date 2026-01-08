import asyncio
from telethon import TelegramClient, events
from .. import logger


class TelegramService:

    def __init__(self, config, message_handler):
        self.config = config
        self.message_handler = message_handler

        self.client = TelegramClient(
            session='signal_watchdog_session',
            api_id=self.config['telegram_api_id'],
            api_hash=self.config['telegram_api_hash'],
            system_version="4.16.30-vxCUSTOM",
            device_model="zalupka 5G"
        )

    async def monitor_channels(self):
        channels = self.config['channels']

        for group_name, channel_id in channels.items():
            try:
                entity = await self.client.get_entity(channel_id)
                logger.info(f"Мониторинг группы {group_name}: {channel_id}")

                @self.client.on(events.NewMessage(chats=entity))
                async def handler(event, group=group_name):
                    await self.message_handler(event, group)
                    # FIXME: Telethon НЕ удаляет старые хендлеры
                    # при reload_config() или повторном start()

                    # добавить глобальный хендлер.

            except Exception as e:
                logger.error(
                    f"Не удалось подключиться к группе "
                    f"{group_name} ({channel_id}): {e}"
                )

    async def start(self):
        # До: была возможная потеря сообщений при запуске бота
        # поскольку клиент создавался до хендлеров.
        # :DONE:
        logger.info("Подключение Хендлеров и запуск Telegram клиента...")

        await self.monitor_channels()

        logger.info("Все хендлеры подключены.")

        await self.client.start()

        logger.info("Telegram клиент подключен.")

        me = await self.client.get_me()
        logger.info(f"Вошли как: {me.username or me.phone}")

        logger.info("Telegram клиент запущен и слушает каналы")

