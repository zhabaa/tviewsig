import asyncio
import sys

from core.watchdog import TelegramWatchdog

from . import logger


async def main():
    """Основная функция запуска бота"""
    watchdog = None
    
    try:
        watchdog = TelegramWatchdog()
        await watchdog.start()

    except KeyboardInterrupt:
        logger.info("Работа завершена пользователем")
        return

    except Exception as ex:
        logger.error(f"Critical Error: {ex}", exc_info=True)
        raise ex

    finally:
        if watchdog is not None and hasattr(watchdog, 'client'):

            if watchdog.client.is_connected():
                await watchdog.client.disconnect()


if __name__ == "__main__":
    """
    Для Windows нужно использовать asyncio.run()
    """

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Приложение завершено")

    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}")
        sys.exit(1)  # Возвращаем код ошибки
