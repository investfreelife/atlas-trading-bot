"""Futures intraday strategy example."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, time
from typing import List, Optional

import pandas as pd

from .trading_strategies import Signal


@dataclass
class Candle:
    """Market candle data."""

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class FuturesIntradayStrategy:
    """Very simple intraday futures strategy using ATR for SL/TP."""

    def __init__(self, symbol: str = "BTCUSDT", atr_period: int = 14) -> None:
        self.symbol = symbol
        self.atr_period = atr_period
        self.candles: List[Candle] = []
        self.last_signal: Optional[Signal] = None

    def add_candle(self, candle: Candle) -> None:
        """Add new candle to the history."""
        self.candles.append(candle)
        # keep history limited
        max_len = self.atr_period * 2
        if len(self.candles) > max_len:
            self.candles = self.candles[-max_len:]

    def _compute_atr(self) -> Decimal:
        """Compute ATR using the stored candles."""
        if len(self.candles) <= self.atr_period:
            return Decimal("0")

        df = pd.DataFrame(
            {
                "high": [float(c.high) for c in self.candles],
                "low": [float(c.low) for c in self.candles],
                "close": [float(c.close) for c in self.candles],
            }
        )
        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift()).abs()
        low_close = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr_series = tr.rolling(self.atr_period).mean()
        atr_value = atr_series.iloc[-1]
        return Decimal(str(round(float(atr_value), 8)))

    def analyze_market(self) -> Optional[Signal]:
        """Check last candle and generate signal if breakout occurs."""
        if len(self.candles) <= self.atr_period:
            return None

        last_candle = self.candles[-1]
        now = last_candle.timestamp.time()
        if time(0, 0) <= now <= time(7, 0):
            # no-trade zone
            return None

        atr = self._compute_atr()
        if atr == 0:
            return None

        previous_high = max(c.high for c in self.candles[-4:-1])
        previous_volume = self.candles[-2].volume

        if last_candle.close > previous_high and last_candle.volume > previous_volume:
            entry = last_candle.close
            signal = Signal(
                symbol=self.symbol,
                action="buy",
                confidence=0.6,
                reason="Breakout with volume",
                entry_price=entry,
                stop_loss=entry - atr * Decimal("1.2"),
                take_profit=entry + atr * Decimal("2.4"),
            )
            self.last_signal = signal
            return signal
        return None
