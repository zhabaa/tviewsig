import re
from datetime import datetime
from .. import logger


class SignalParser:

    def __init__(self, config, channel_mapping, total_parsers, bitcoin_parsers, eth_parsers):
        self.config = config
        self.channel_mapping = channel_mapping

        self.signal_parsers = [
            {
                'name': 'total_main_signal',
                'regex': re.compile(r'([🟥🟩]) TOTAL (SHORT|LONG) (\d+)', re.IGNORECASE),
                'group': 'TOTAL',
                'parse_func': total_parsers.parse_total_signal
            },
            {
                'name': 'total_alts_combo',
                'regex': re.compile(
                    r'([🔴🟢]+) TTL \(ALTS\) (SHORT|LONG) COMBO (\d+)', re.IGNORECASE
                ),
                'group': 'TOTAL',
                'parse_func': total_parsers.parse_total_alts_signal
            },
            {
                'name': 'total_report',
                'regex': re.compile(
                    r'Ⓜ️ TSB (LONG|SHORT) Report #(\d+/\d+)', re.IGNORECASE
                ),
                'group': 'TOTAL',
                'parse_func': total_parsers.parse_total_report
            },
            {
                'name': 'bitcoin_combo',
                'regex': re.compile(
                    r'([🟢]+) (LONG COMBO (\d+)|🧠 BTC Signal)', re.IGNORECASE
                ),
                'group': 'BITCOIN',
                'parse_func': bitcoin_parsers.parse_bitcoin_signal
            },
            {
                'name': 'bitcoin_zone_signal',
                'regex': re.compile(
                    r'Стратегия: ZONE\s+Уровень: (\d+)\s+Направление: (LONG|SHORT)',
                    re.IGNORECASE
                ),
                'group': 'BITCOIN',
                'parse_func': bitcoin_parsers.parse_bitcoin_zone_signal
            },
            {
                'name': 'eth_ai_signal',
                'regex': re.compile(
                    r'🧠 ETH AI v2\s+Стратегия: (\w+)\s+Уровень: (\d+)\s+Тип: (\w+)'
                    r'\s+Направление: ([🔴🟢]+)(LONG|SHORT)',
                    re.IGNORECASE
                ),
                'group': 'ETH',
                'parse_func': eth_parsers.parse_eth_signal
            },
            {
                'name': 'eth_price_extract',
                'regex': re.compile(
                    r'(BTC|ETH)/USDT-SPOT:\s*([\d,]+\.?\d*)',
                    re.IGNORECASE
                ),
                'group': 'ALL',
                'parse_func': lambda m, t, g: None
            }
        ]

    async def parse_signal(self, text: str, channel_name: str, group_type: str):
        text_lower = text.lower()

        skip_keywords = self.config['parse_rules']['skip_keywords']
        if any(keyword.lower() in text_lower for keyword in skip_keywords):
            return None

        group = group_type
        if not group:
            if 'eth' in text_lower or 'ETH/USDT' in text:
                group = 'ETH'
            elif 'ttl' in text_lower or 'total' in text_lower:
                group = 'TOTAL'
            elif 'btc' in text_lower or 'BTC/USDT' in text:
                group = 'BITCOIN'

        for parser in self.signal_parsers:
            if parser['group'] == group or parser['group'] == 'ALL':
                match = parser['regex'].search(text)
                if match:
                    try:
                        signal = parser['parse_func'](match, text, group)
                        if signal:
                            signal['timestamp'] = datetime.utcnow().isoformat()
                            signal['channel'] = channel_name

                            logger.info(
                                f"Найден сигнал в {group}: "
                                f"{signal['action']} {signal['symbol']}"
                            )
                            return signal
                    except Exception as e:
                        logger.warning(
                            f"Ошибка в парсере {parser['name']}: {e}, "
                            f"текст: {text[:50]}..."
                        )
                        continue

        return None
