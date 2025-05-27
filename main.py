"""
Главный API сервер торгового бота
"""
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, List
import uvicorn

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Импортируем наши модули
from shared.trading_strategies import Signal, OrderSide
from shared.simple_strategy import SimpleStrategy

# Создаем FastAPI приложение
app = FastAPI(
    title="Trading Bot API",
    description="API для торгового бота",
    version="1.0.0"
)


# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Веб-интерфейс дашборда"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Dashboard not found. Create static/index.html</h1>")

# Глобальные переменные
strategy = SimpleStrategy()
active_signals: List[Signal] = []


@app.get("/")
async def root():
    """Главная страница"""
    return {
        "message": "🤖 Trading Bot API",
        "status": "running",
        "time": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "strategy": "active",
            "api": "running",
            "database": "not connected"  # пока без БД
        }
    }


@app.get("/market/price/{symbol}")
async def get_price(symbol: str):
    """Получить текущую цену"""
    if symbol.upper() != "BTCUSDT":
        raise HTTPException(status_code=404, detail="Symbol not found")

    return {
        "symbol": symbol.upper(),
        "price": float(strategy.get_current_price()),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/strategy/analyze")
async def analyze_market():
    """Запустить анализ рынка"""
    signal = strategy.analyze_market()

    if signal:
        # Добавляем сигнал в список активных
        active_signals.append(signal)

        return {
            "signal_generated": True,
            "signal": {
                "symbol": signal.symbol,
                "action": signal.action,
                "confidence": signal.confidence,
                "reason": signal.reason,
                "entry_price": float(signal.entry_price) if signal.entry_price else None,
                "stop_loss": float(signal.stop_loss) if signal.stop_loss else None,
                "take_profit": float(signal.take_profit) if signal.take_profit else None
            },
            "current_price": float(strategy.get_current_price())
        }
    else:
        return {
            "signal_generated": False,
            "message": "No trading signals at this time",
            "current_price": float(strategy.get_current_price())
        }


@app.get("/signals/active")
async def get_active_signals():
    """Получить активные сигналы"""
    return {
        "count": len(active_signals),
        "signals": [
            {
                "symbol": s.symbol,
                "action": s.action,
                "confidence": s.confidence,
                "reason": s.reason
            } for s in active_signals[-10:]  # Последние 10
        ]
    }


@app.get("/bot/status")
async def bot_status():
    """Статус торгового бота"""
    return {
        "bot_active": True,
        "strategy_type": "SimpleStrategy",
        "total_signals": len(active_signals),
        "current_price": float(strategy.get_current_price()),
        "uptime": "running"
    }


if __name__ == "__main__":
    print("🚀 Запускаем Trading Bot API...")
    print("📡 API будет доступен на: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Автоперезагрузка при изменениях
        log_level="info"
    )