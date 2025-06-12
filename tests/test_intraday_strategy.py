from datetime import datetime, timedelta
from decimal import Decimal

from shared.futures_intraday_strategy import Candle, FuturesIntradayStrategy


def create_candle(price: float, volume: float, ts: datetime) -> Candle:
    return Candle(
        timestamp=ts,
        open=Decimal(str(price)),
        high=Decimal(str(price * 1.01)),
        low=Decimal(str(price * 0.99)),
        close=Decimal(str(price)),
        volume=Decimal(str(volume)),
    )


def test_breakout_signal():
    strategy = FuturesIntradayStrategy(atr_period=3)
    base_time = datetime(2023, 1, 1, 8, 0, 0)
    prices = [100, 101, 102, 105]
    volumes = [10, 10, 10, 20]
    for i, p in enumerate(prices):
        candle = create_candle(p, volumes[i], base_time + timedelta(minutes=i))
        strategy.add_candle(candle)

    signal = strategy.analyze_market()
    assert signal is not None
    assert signal.action == "buy"
    assert signal.entry_price == strategy.candles[-1].close
