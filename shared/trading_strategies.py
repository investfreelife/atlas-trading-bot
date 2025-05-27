"""
Базовые торговые стратегии
"""
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

class OrderSide(Enum):
    """Направление ордера"""
    BUY = "buy"
    SELL = "sell"

@dataclass
class Signal:
    """Торговый сигнал"""
    symbol: str
    action: str  # "buy", "sell", "hold"
    confidence: float  # 0.0 - 1.0
    reason: str
    entry_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None

def test_strategy():
    """Простая тестовая функция"""
    signal = Signal(
        symbol="BTCUSDT",
        action="buy",
        confidence=0.8,
        reason="Test signal"
    )
    print(f"Created signal: {signal}")
    return signal

if __name__ == "__main__":
    test_strategy()