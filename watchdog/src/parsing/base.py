import re
from typing import Optional
from functions import SignalStrengthDetector
from .. import logger


class BaseParsingUtils:

    @staticmethod
    def extract_price(text: str) -> Optional[float]:
        price_match = re.search(r'(BTC|ETH)/USDT-SPOT:\s*([\d,]+\.?\d*)', text)

        if price_match:
            try:
                price_str = price_match.group(2).replace(',', '')
                return float(price_str)
            except Exception as ex:
                logger.warning(
                    f"Error while price extraction: {ex}, returned NoneType\n Текст: {text[:67]}..."
                )
                return None
        return None

    @staticmethod
    def determine_signal_strength(emoji_count: int, text: str) -> int:
        strength = emoji_count
        text_lower = text.lower()

        for pattern, pattern_strength in SignalStrengthDetector.PATTERNS.items():
            if pattern in text_lower:
                strength = max(strength, pattern_strength)

        return min(strength, 3)
