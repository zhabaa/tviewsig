import re
from .. import logger
from .base import BaseParsingUtils


class BitcoinParsers(BaseParsingUtils):
    def __init__(self, channel_mapping):
        self.channel_to_bot_mapping = channel_mapping

    def parse_bitcoin_signal(self, match, text, group):
        try:
            emojis = match.group(1)
            signal_text = match.group(2)

            if "LONG COMBO" in signal_text:
                combo_match = re.search(r"LONG COMBO (\d+)", signal_text)
                strength = int(combo_match.group(1)) if combo_match else len(emojis)
                action = "BUY"
                signal_type = f"LONG_COMBO_{strength}"

            else:
                action = "BUY"
                signal_type = "BTC_SIGNAL"
                strength = len(emojis)

            price = self.extract_price(text)

            horizon_match = re.search(r"Горизонт:\s*(.+?)(?:\s*\|?\s*Цель:|$)", text)
            horizon = horizon_match.group(1).strip() if horizon_match else ""

            target_match = re.search(r"Цель:\s*(.+?)(?:\n|$)", text)
            target = target_match.group(1).strip() if target_match else ""

            return {
                "bot_name": self.channel_to_bot_mapping[group],
                "symbol": "BTC/USDT",
                "action": action,
                "price": price,
                "strength": strength,
                "signal_type": signal_type,
                "horizon": horizon,
                "target": target,
                "source": group,
                "raw_text": text[:500],
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга BITCOIN сигнала: {e}")
            return None

    def parse_bitcoin_zone_signal(self, match, text, group):
        try:
            level = int(match.group(1))
            action = match.group(2).upper()

            strength = level
            price = self.extract_price(text)

            strategy_match = re.search(r"Стратегия:\s*(\w+)", text)
            strategy = strategy_match.group(1) if strategy_match else "ZONE"

            return {
                "bot_name": self.channel_to_bot_mapping[group],
                "symbol": "BTC/USDT",
                "action": "BUY" if "LONG" in action else "SELL",
                "price": price,
                "strength": strength,
                "signal_type": f"ZONE_LEVEL_{level}",
                "strategy": strategy,
                "source": group,
                "raw_text": text[:500],
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга BITCOIN ZONE сигнала: {e}")
            return None
