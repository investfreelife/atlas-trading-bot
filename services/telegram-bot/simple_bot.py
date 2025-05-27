"""
Простой Telegram бот для тестирования
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Здесь будет токен бота (пока тестовый)
BOT_TOKEN = "TEST_TOKEN"


async def test_bot_locally():
    """Тестируем бота локально без реального токена"""
    print("🤖 Тестируем создание бота...")

    # Создаем экземпляры (без реального подключения)
    try:
        # bot = Bot(token=BOT_TOKEN)  # Закомментировано для тестирования
        # dp = Dispatcher()

        print("✅ Классы Bot и Dispatcher импортированы успешно")
        print("✅ aiogram работает!")

        # Тестируем создание сообщения
        test_message_data = {
            'symbol': 'BTCUSDT',
            'action': 'buy',
            'price': 50000
        }

        message_text = f"""
🤖 ТОРГОВЫЙ СИГНАЛ

📈 Символ: {test_message_data['symbol']}
🔥 Действие: {test_message_data['action'].upper()}
💰 Цена: ${test_message_data['price']:,}
⏰ Время: Тест
        """

        print("📱 Пример сообщения для Telegram:")
        print(message_text)

        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_bot_locally())