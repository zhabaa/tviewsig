import asyncio
from .. import logger

AVAILABLE_COMMANDS = """
Доступные команды:
stats - Показать статистику
channels - Список каналов
test [группа] [текст] - Тестовый парсинг текста
reload - Перезагрузить конфигурацию
exit - Выход
"""


class InteractiveConsole:
    def __init__(self, watchdog):
        self.watchdog = watchdog

    async def run(self):
        while True:
            try:
                command = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\n> Введите команду (help для справки): "
                )

                print()

                command_lower = command.lower()

                match command_lower:
                    case "help":
                        print(AVAILABLE_COMMANDS)

                    case "stats":
                        print("📊 Текущая статистика:")

                        for key, value in self.watchdog.stats.__dict__.items():
                            print(f"  {key}: {value}")

                    case "channels":
                        print("📢 Мониторинг групп:")

                        for group, channel in self.watchdog.config["channels"].items():
                            print(f" - {group}: {channel}")

                    case command_lower if command_lower.startswith("test "):
                        parts = command.split(" ", 2)

                        if len(parts) >= 3:
                            group = parts[1].upper()
                            test_text = parts[2]

                            signal = await self.watchdog.parser.parse_signal(
                                test_text, "test_channel", group
                            )

                            if signal:
                                print(f"\n✅ Найден сигнал в группе {group}:")
                                for key, value in signal.items():
                                    print(f"  {key}: {value}")
                            else:
                                print(
                                    f"\n❌ Сигнал не найден в тексте для группы {group}"
                                )
                        else:
                            print("\n❌ Формат: test [TOTAL|BITCOIN|ETH] [текст]")

                    case "reload":
                        self.watchdog.reload_config()
                        print("✅ Конфигурация перезагружена")

                    case "exit":
                        print("👋 Завершение работы...")
                        await self.watchdog.telegram.client.disconnect()
                        break

                    case _:
                        print(f"❌ Неизвестная команда: {command}")

            except KeyboardInterrupt:
                print("👋 Завершение работы...")
                await self.watchdog.telegram.client.disconnect()
                break

            except Exception as e:
                logger.error(f"Ошибка в консоли: {e}")
