"""
Простая торговая стратегия для тестирования
"""
from decimal import Decimal
from datetime import datetime
from typing import Optional
import random

from shared.trading_strategies import Signal


class SimpleStrategy:
    """Простая стратегия для демонстрации"""

    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.last_price = Decimal("50000")  # Начальная цена

    def analyze_market(self) -> Optional[Signal]:
        """Анализ рынка и генерация сигнала"""

        # Симулируем изменение цены
        change = random.uniform(-0.02, 0.02)  # ±2%
        self.last_price = self.last_price * Decimal(str(1 + change))

        # Простая логика: если цена упала > 1%, покупаем
        if change < -0.01:
            return Signal(
                symbol=self.symbol,
                action="buy",
                confidence=0.7,
                reason=f"Price dropped {change:.2%}, good buying opportunity",
                entry_price=self.last_price,
                stop_loss=self.last_price * Decimal("0.95"),  # -5% стоп
                take_profit=self.last_price * Decimal("1.03")  # +3% профит
            )

        # Если цена выросла > 1.5%, продаем
        elif change > 0.015:
            return Signal(
                symbol=self.symbol,
                action="sell",
                confidence=0.6,
                reason=f"Price rose {change:.2%}, time to take profit",
                entry_price=self.last_price
            )

        return None

    def get_current_price(self) -> Decimal:
        """Получить текущую цену"""
        return self.last_price


def test_strategy():
    """Тестирование стратегии"""
    print("🧠 Тестируем торговую стратегию...")

    strategy = SimpleStrategy()

    print(f"💰 Начальная цена: ${strategy.get_current_price():,}")

    # Тестируем 5 итераций
    for i in range(5):
        signal = strategy.analyze_market()
        current_price = strategy.get_current_price()

        print(f"\n📊 Итерация {i + 1}:")
        print(f"💰 Цена: ${current_price:,}")

        if signal:
            print(f"🎯 СИГНАЛ: {signal.action.upper()}")
            print(f"📝 Причина: {signal.reason}")
            print(f"🎯 Уверенность: {signal.confidence:.1%}")
            if signal.entry_price:
                print(f"💵 Цена входа: ${signal.entry_price:,}")
        else:
            print("😴 Сигналов нет, ждем...")


if __name__ == "__main__":
    test_strategy()