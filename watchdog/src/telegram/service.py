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

            except Exception as e:
                logger.error(
                    f"Не удалось подключиться к группе "
                    f"{group_name} ({channel_id}): {e}"
                )

    async def start(self):
        logger.info("Запуск Telegram клиента...")

        await self.client.start()

        me = await self.client.get_me()
        logger.info(f"Вошли как: {me.username or me.phone}")

        await self.monitor_channels()

        logger.info("Telegram клиент запущен и слушает каналы")
