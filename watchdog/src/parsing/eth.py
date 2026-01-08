import re
from .. import logger


class EthParsers:

    def __init__(self, channel_mapping):
        self.channel_to_bot_mapping = channel_mapping

    def parse_eth_signal(self, match, text, group):
        try:
            strategy = match.group(1)
            level = int(match.group(2))
            signal_type = match.group(3)
            emoji = match.group(4)
            action = match.group(5).upper()

            strength = level

            price_match = re.search(
                r'ETH/USDT-SPOT:\s*([\d,]+\.?\d*)', text
            )
            price = float(price_match.group(1).replace(',', '')) if price_match else None

            strength_match = re.search(
                r'Сила сигнала:.+?(\d+)\s*/\s*100', text
            )
            ai_strength = int(strength_match.group(1)) if strength_match else None

            conclusion_match = re.search(
                r'Вывод:\s*(.+?)(?:\n|$)', text
            )
            conclusion = conclusion_match.group(1).strip() if conclusion_match else ""

            return {
                'bot_name': self.channel_to_bot_mapping[group],
                'symbol': 'ETH/USDT',
                'action': 'BUY' if 'LONG' in action else 'SELL',
                'price': price,
                'strength': strength,
                'ai_strength': ai_strength,
                'signal_type': f'ETH_AI_{strategy}_LEVEL_{level}',
                'eth_signal_type': signal_type,
                'conclusion': conclusion,
                'source': group,
                'raw_text': text[:500]
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга ETH сигнала: {e}")
            return None
