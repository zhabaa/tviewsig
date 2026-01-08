import asyncio
from .. import logger


class InteractiveConsole:

    def __init__(self, watchdog):
        self.watchdog = watchdog

    async def run(self):
        while True:
            try:
                command = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\n> Введите команду (help для справки): "
                )

                if command.lower() == 'help':
                    print("\nДоступные команды:")
                    print("  stats - Показать статистику")
                    print("  channels - Список каналов")
                    print("  test [группа] [текст] - Тестовый парсинг текста")
                    print("  reload - Перезагрузить конфигурацию")
                    print("  exit - Выход")

                elif command.lower() == 'stats':
                    print("\n📊 Текущая статистика:")
                    for key, value in self.watchdog.stats.__dict__.items():
                        print(f"  {key}: {value}")

                elif command.lower() == 'channels':
                    print("\n📢 Мониторинг групп:")
                    for group, channel in self.watchdog.config['channels'].items():
                        print(f"  - {group}: {channel}")

                elif command.lower().startswith('test '):
                    parts = command.split(' ', 2)
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
                                f"\n❌ Сигнал не найден в тексте "
                                f"для группы {group}"
                            )
                    else:
                        print("\n❌ Формат: test [TOTAL|BITCOIN|ETH] [текст]")

                elif command.lower() == 'reload':
                    self.watchdog.reload_config()
                    print("\n✅ Конфигурация перезагружена")

                elif command.lower() == 'exit':
                    print("\n👋 Завершение работы...")
                    await self.watchdog.telegram.client.disconnect()
                    break

                else:
                    print(f"\n❌ Неизвестная команда: {command}")

            except KeyboardInterrupt:
                print("\n👋 Завершение работы...")
                await self.watchdog.telegram.client.disconnect()
                break

            except Exception as e:
                logger.error(f"Ошибка в консоли: {e}")
