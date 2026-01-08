import re
from .. import logger
from .base import BaseParsingUtils


class TotalParsers(BaseParsingUtils):

    def __init__(self, channel_mapping):
        self.channel_to_bot_mapping = channel_mapping

    def parse_total_signal(self, match, text, group):
        try:
            emoji = match.group(1)
            action = match.group(2).upper()
            signal_number = int(match.group(3))

            strength = 1
            if '🟥' in emoji or '🟩' in emoji:
                strength = signal_number

            price = self.extract_price(text)

            description_match = re.search(
                r'Описание:\s*(.+?)(?:\n\n|\n___|$)', text, re.DOTALL
            )
            description = description_match.group(1).strip() if description_match else ""

            expectation_match = re.search(r'Ожидания:\s*(.+?)(?:\n|$)', text)
            expectations = expectation_match.group(1).strip() if expectation_match else ""

            return {
                'bot_name': self.channel_to_bot_mapping[group],
                'symbol': 'BTC/USDT',
                'action': 'SELL' if 'SHORT' in action else 'BUY',
                'price': price,
                'strength': strength,
                'signal_type': f'TOTAL_{action}_{signal_number}',
                'description': description,
                'expectations': expectations,
                'source': group,
                'raw_text': text[:500]
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга TOTAL сигнала: {e}")
            return None

    def parse_total_alts_signal(self, match, text, group):
        try:
            emojis = match.group(1)
            action = match.group(2).upper()
            combo_number = int(match.group(3))

            strength = len(emojis)
            price = self.extract_price(text)

            notes_match = re.search(r'Примечания:\s*(.+?)(?:\n|$)', text)
            notes = notes_match.group(1).strip() if notes_match else ""

            return {
                'bot_name': self.channel_to_bot_mapping[group],
                'symbol': 'ALTS/USDT',
                'action': 'SELL' if 'SHORT' in action else 'BUY',
                'price': price,
                'strength': strength,
                'signal_type': f'TTL_ALTS_{action}_COMBO_{combo_number}',
                'notes': notes,
                'source': group,
                'raw_text': text[:500]
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга TTL ALTS сигнала: {e}")
            return None

    def parse_total_report(self, match, text, group):
        try:
            action = match.group(1).upper()
            report_number = match.group(2)

            strength = 1
            if 'отличная зона' in text.lower():
                strength = 3
            elif 'хорошая зона' in text.lower():
                strength = 2

            price = self.extract_price(text)

            bid_match = re.search(r'BID строки\s*[>]?\s*(\d+)', text)
            bid_lines = int(bid_match.group(1)) if bid_match else 0

            growth_match = re.search(
                r'Расчетный (?:рост|отскок).*?(\d+(?:-\d+)?%)', text
            )
            expected_growth = growth_match.group(1) if growth_match else ""

            return {
                'bot_name': self.channel_to_bot_mapping[group],
                'symbol': 'ALTS/USDT',
                'action': 'BUY' if 'LONG' in action else 'SELL',
                'price': price,
                'strength': strength,
                'signal_type': f'TSB_REPORT_{report_number}',
                'bid_lines': bid_lines,
                'expected_growth': expected_growth,
                'source': group,
                'raw_text': text[:500]
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга TSB отчета: {e}")
            return None
