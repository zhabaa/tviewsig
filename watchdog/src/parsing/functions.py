from typing import Dict


class SignalStrengthDetector:
    """
    Словарь с паттернами и их весом
    """
    
    PATTERNS: Dict[str, int] = {
        # ru
        'супер': 3, 'отличная': 3, 'идеально': 3,
        'хорошая': 2, 'рекомендую': 2, 'стабильный': 2,
        'слабый': 1, 'вероятно': 1, 'осторожно': 1,
        # en
        'super': 3, 'excellent': 3, 'perfect': 3,
        'good': 2, 'recommend': 2, 'stable': 2,
        'weak': 1, 'probably': 1, 'caution': 1,
    }
