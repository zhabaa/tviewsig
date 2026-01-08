import aiohttp
import asyncio
from datetime import datetime
from .. import logger


class ApiSender:
    def __init__(self, api_url, api_key, config, stats):
        self.api_url = api_url
        self.api_key = api_key
        self.config = config
        self.stats = stats

    async def send(self, signal: dict) -> bool:
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }

        payload = {
            'bot_name': signal['bot_name'],
            'symbol': signal['symbol'],
            'action': signal['action'],
            'price': signal.get('price'),
            'timestamp': signal.get('timestamp', datetime.utcnow().isoformat()),
            'strength': signal.get('strength', 1),
            'signal_type': signal.get('signal_type', 'UNKNOWN'),
            'source': signal.get('source', 'UNKNOWN'),
            'channel': signal.get('channel', ''),
            'metadata': {}
        }

        metadata_fields = [
            'description', 'expectations', 'notes', 'horizon',
            'target', 'strategy', 'conclusion', 'expected_growth',
            'ai_strength', 'bid_lines', 'eth_signal_type'
        ]

        for field in metadata_fields:
            if field in signal and signal[field]:
                payload['metadata'][field] = signal[field]

        for attempt in range(self.config['monitoring']['retry_attempts']):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.api_url,
                        json=payload,
                        headers=headers,
                        timeout=10
                    ) as response:

                        if response.status == 201:
                            self.stats.signals_sent += 1
                            logger.info(
                                f"Сигнал успешно отправлен: "
                                f"{signal['symbol']} ({signal['signal_type']})"
                            )
                            return True
                        elif response.status == 401:
                            logger.error("Неверный API ключ!")
                            return False
                        else:
                            logger.warning(
                                f"Ошибка API: {response.status}, "
                                f"попытка {attempt + 1}"
                            )

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(
                    f"Сетевая ошибка: {e}, попытка {attempt + 1}"
                )

            if attempt < self.config['monitoring']['retry_attempts'] - 1:
                await asyncio.sleep(self.config['monitoring']['retry_delay'])

        self.stats.errors += 1
        return False
