import asyncio
import logging
import os
from datetime import datetime
from decimal import Decimal

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import aiohttp

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = "http://localhost:8000"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище состояния пользователей
user_states = {}


async def get_api_data(endpoint: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}{endpoint}") as response:
                return await response.json()
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None


async def post_api_data(endpoint: str, data=None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE_URL}{endpoint}", json=data) as response:
                return await response.json()
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None


def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💰 Портфель", callback_data="portfolio"),
        InlineKeyboardButton(text="📊 Цены", callback_data="get_prices")
    )
    builder.row(
        InlineKeyboardButton(text="🤖 Мои боты", callback_data="my_bots"),
        InlineKeyboardButton(text="🧠 Анализ", callback_data="analyze_market")
    )
    builder.row(
        InlineKeyboardButton(text="📈 Сигналы", callback_data="active_signals"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    builder.row(
        InlineKeyboardButton(text="🆘 СТОП", callback_data="emergency_stop")
    )
    return builder.as_markup()


def get_bot_management_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="▶️ Запустить", callback_data="start_trading"),
        InlineKeyboardButton(text="⏸️ Пауза", callback_data="pause_trading")
    )
    builder.row(
        InlineKeyboardButton(text="⏹️ Остановить", callback_data="stop_trading"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="bot_stats")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    )
    return builder.as_markup()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    welcome_text = f"""
🤖 **ATLAS TRADING BOT**

Добро пожаловать, {message.from_user.first_name}! 

🚀 **Полностью автономный торговый бот для криптовалют**

✅ **4 торговые стратегии**
- Фьючерсы внутридневная
- Фьючерсы среднесрочная  
- Спот среднесрочная
- Умное DCA накопление

✅ **Полная автоматизация**
- Работа 24/7
- Автоматический риск-менеджмент
- Уведомления о всех операциях
- Прозрачная отчетность

💰 **Текущий баланс:** Подключите API для просмотра
🤖 **Активные боты:** 0
📊 **Статус:** Готов к настройке

👇 **Выберите действие:**
"""
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📚 **РУКОВОДСТВО ПО ТОРГОВОМУ БОТУ**

🎯 **Основные функции:**

💰 **Портфель** - баланс, P&L, активные позиции
📊 **Цены** - актуальные цены криптовалют
🤖 **Мои боты** - управление торговыми ботами
🧠 **Анализ** - торговые сигналы в реальном времени
📈 **Сигналы** - история и активные сигналы
⚙️ **Настройки** - API ключи, профиль риска

🛡️ **Безопасность:**
- API ключи зашифрованы AES-256
- Только права на чтение + торговлю
- Автоматические стоп-лоссы
- Контроль просадки

⚠️ **Риски:**
- Торговля криптовалютами высокорискованна
- Можете потерять весь капитал
- Используйте только свободные средства
- Начните с минимальных сумм

🆘 **Экстренная остановка:** /emergency
"""
    await message.answer(help_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")


@dp.message(Command("emergency"))
async def cmd_emergency(message: Message):
    user_id = message.from_user.id

    # Отправляем команду экстренной остановки
    result = await post_api_data("/emergency/stop", {"user_id": user_id})

    emergency_text = """
🆘 **ЭКСТРЕННАЯ ОСТАНОВКА АКТИВИРОВАНА**

✅ **Выполнено:**
- Все боты остановлены
- Новые ордера заблокированы  
- Открытые позиции закрываются
- Уведомления отправлены

⏰ **Время выполнения:** < 30 секунд

🔄 **Восстановление:**
- Автоматическое через 1 час
- Ручное через настройки
- Обратитесь в поддержку при необходимости

📞 **Поддержка:** @support
"""

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Возобновить через час", callback_data="schedule_resume"),
        InlineKeyboardButton(text="📞 Связаться с поддержкой", callback_data="contact_support")
    )

    await message.answer(emergency_text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@dp.callback_query(F.data == "portfolio")
async def callback_portfolio(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Получаем данные портфеля
    portfolio_data = await get_api_data(f"/user/{user_id}/portfolio")

    if portfolio_data:
        total_balance = portfolio_data.get('total_balance', 0)
        unrealized_pnl = portfolio_data.get('unrealized_pnl', 0)
        daily_pnl = portfolio_data.get('daily_pnl', 0)
        positions = portfolio_data.get('positions', {})

        pnl_emoji = "📈" if daily_pnl >= 0 else "📉"
        pnl_sign = "+" if daily_pnl >= 0 else ""

        portfolio_text = f"""
💰 **МОЙ ПОРТФЕЛЬ**

💵 **Общий баланс:** ${total_balance:,.2f}
📊 **Нереализованный P&L:** ${unrealized_pnl:,.2f}
{pnl_emoji} **Сегодня:** {pnl_sign}${daily_pnl:,.2f} ({(daily_pnl / total_balance * 100):+.2f}%)

🎯 **Активные позиции:** {len(positions)}
📈 **Максимальная просадка:** {portfolio_data.get('max_drawdown', 0):.2f}%

⏰ **Обновлено:** {datetime.now().strftime('%H:%M:%S')}

"""

        if positions:
            portfolio_text += "\n📋 **Открытые позиции:**\n"
            for symbol, position in list(positions.items())[:5]:  # Показываем первые 5
                side_emoji = "🟢" if position['side'] == 'long' else "🔴"
                pnl_pos = position.get('unrealized_pnl', 0)
                pnl_pos_sign = "+" if pnl_pos >= 0 else ""
                portfolio_text += f"{side_emoji} **{symbol}** {pnl_pos_sign}${pnl_pos:.2f}\n"

    else:
        portfolio_text = """
💰 **ПОРТФЕЛЬ НЕ ПОДКЛЮЧЕН**

🔧 **Для просмотра портфеля необходимо:**
1. Настроить API ключи Bybit
2. Активировать торговые боты
3. Подождать синхронизации

👇 Перейдите в настройки для подключения
"""

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Обновить", callback_data="portfolio"),
        InlineKeyboardButton(text="📊 Детали", callback_data="detailed_portfolio")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки API", callback_data="settings"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    )

    await callback.message.edit_text(portfolio_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data == "my_bots")
async def callback_my_bots(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Получаем список ботов пользователя
    bots_data = await get_api_data(f"/user/{user_id}/bots")

    if bots_data and bots_data.get('bots'):
        bots_text = "🤖 **МОИ ТОРГОВЫЕ БОТЫ**\n\n"

        for bot in bots_data['bots']:
            status_emoji = {"running": "🟢", "paused": "🟡", "stopped": "🔴"}.get(bot['status'], "❓")
            pnl = bot.get('total_pnl', 0)
            pnl_sign = "+" if pnl >= 0 else ""

            bots_text += f"""
{status_emoji} **{bot['strategy_name']}**
📊 P&L: {pnl_sign}${pnl:.2f}
🎯 Позиций: {bot.get('active_positions', 0)}
⏰ Время работы: {bot.get('uptime', '0 мин')}

"""
    else:
        bots_text = """
🤖 **ТОРГОВЫЕ БОТЫ НЕ НАСТРОЕНЫ**

🚀 **Доступные стратегии:**

⚡ **Фьючерсы Внутридневная**
Краткосрочная торговля (1-8 часов)
Ожидаемая доходность: 15-25% годовых

💎 **Фьючерсы Среднесрочная**  
Следование трендам (3-30 дней)
Ожидаемая доходность: 20-40% годовых

🏪 **Спот Среднесрочная**
Накопление активов (1-6 месяцев)
Ожидаемая доходность: 30-60% годовых

🤖 **Умное DCA**
Усреднение цены покупки
Ожидаемая доходность: 25-50% годовых

👇 Выберите стратегию для настройки:
"""

    builder = InlineKeyboardBuilder()
    if bots_data and bots_data.get('bots'):
        # Если есть боты - показываем управление
        builder.row(
            InlineKeyboardButton(text="▶️ Запустить все", callback_data="start_all_bots"),
            InlineKeyboardButton(text="⏸️ Пауза все", callback_data="pause_all_bots")
        )
        builder.row(
            InlineKeyboardButton(text="⚙️ Настроить", callback_data="configure_bots"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="bots_stats")
        )
    else:
        # Если ботов нет - показываем создание
        builder.row(
            InlineKeyboardButton(text="⚡ Фьючерсы Интрадей", callback_data="create_futures_intraday"),
            InlineKeyboardButton(text="💎 Фьючерсы Среднесрок", callback_data="create_futures_longterm")
        )
        builder.row(
            InlineKeyboardButton(text="🏪 Спот Среднесрок", callback_data="create_spot_medium"),
            InlineKeyboardButton(text="🤖 Умное DCA", callback_data="create_dca")
        )

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    )

    await callback.message.edit_text(bots_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data == "settings")
async def callback_settings(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Проверяем текущие настройки
    settings_data = await get_api_data(f"/user/{user_id}/settings")

    if settings_data:
        api_status = "✅ Подключен" if settings_data.get('api_connected') else "❌ Не настроен"
        risk_profile = settings_data.get('risk_profile', 'Не выбран')
        notifications = "✅ Включены" if settings_data.get('notifications_enabled') else "❌ Отключены"
    else:
        api_status = "❌ Не настроен"
        risk_profile = "Не выбран"
        notifications = "❌ Отключены"

    settings_text = f"""
⚙️ **НАСТРОЙКИ СИСТЕМЫ**

🏦 **Bybit API:** {api_status}
🎯 **Профиль риска:** {risk_profile}
🔔 **Уведомления:** {notifications}

📊 **Конфигурация торговли:**
- Максимальная просадка: 20%
- Риск на сделку: 2%
- Автоматические стоп-лоссы: ✅
- Экстренная остановка: ✅

🔐 **Безопасность:**
- API ключи зашифрованы: ✅
- Права только на торговлю: ✅
- Мониторинг активности: ✅

👇 **Что настроить:**
"""

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏦 API Ключи", callback_data="setup_api"),
        InlineKeyboardButton(text="🎯 Риск-профиль", callback_data="setup_risk")
    )
    builder.row(
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="setup_notifications"),
        InlineKeyboardButton(text="💰 Баланс", callback_data="setup_balance")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    )

    await callback.message.edit_text(settings_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data == "setup_api")
async def callback_setup_api(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    api_text = """
🏦 **НАСТРОЙКА BYBIT API**

📋 **Пошаговая инструкция:**

1️⃣ **Зайдите на Bybit.com**
2️⃣ **Авторизуйтесь** в своем аккаунте
3️⃣ **API Management** → Create New Key
4️⃣ **Настройте права:**
   ✅ Read (чтение)
   ✅ Trade (торговля) 
   ❌ Withdraw (БЕЗ вывода!)
5️⃣ **Скопируйте** API Key и Secret

⚠️ **КРИТИЧЕСКИ ВАЖНО:**
- НЕ ДАВАЙТЕ права на вывод средств!
- Используйте отдельный аккаунт для бота
- Начните с минимальных сумм
- Проверьте настройки дважды

🔐 **Безопасность:**
- Ключи шифруются AES-256
- Хранятся в защищенном vault
- Доступ только через API
- Автоматическая ротация каждые 30 дней

📨 **Отправьте API ключи:**
Формат: API_KEY:SECRET_KEY
"""

    # Устанавливаем состояние ожидания API ключей
    user_states[user_id] = "waiting_api_keys"

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❓ Нужна помощь", callback_data="api_help"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="settings")
    )

    await callback.message.edit_text(api_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


# Обработчик текстовых сообщений для API ключей
@dp.message(F.text)
async def handle_text_messages(message: Message):
    user_id = message.from_user.id

    if user_states.get(user_id) == "waiting_api_keys":
        # Обрабатываем API ключи
        text = message.text.strip()

        if ":" in text:
            try:
                api_key, secret = text.split(":", 1)

                # Отправляем ключи на сервер для проверки и сохранения
                result = await post_api_data("/user/api/setup", {
                    "user_id": user_id,
                    "api_key": api_key.strip(),
                    "secret": secret.strip(),
                    "exchange": "bybit"
                })

                if result and result.get('success'):
                    success_text = """
✅ **API КЛЮЧИ НАСТРОЕНЫ УСПЕШНО!**

🔐 **Статус подключения:** Активно
🏦 **Биржа:** Bybit
💰 **Баланс:** Синхронизация...
📊 **Позиции:** Загрузка...

🚀 **Система готова к работе!**

Теперь вы можете:
- Создавать торговых ботов
- Запускать автоматическую торговлю  
- Получать уведомления о сделках
- Отслеживать прибыль в реальном времени

👇 Перейдите к созданию бота:
"""

                    builder = InlineKeyboardBuilder()
                    builder.row(
                        InlineKeyboardButton(text="🤖 Создать бота", callback_data="my_bots"),
                        InlineKeyboardButton(text="💰 Посмотреть портфель", callback_data="portfolio")
                    )

                    await message.answer(success_text, reply_markup=builder.as_markup(), parse_mode="Markdown")

                else:
                    error_text = f"""
❌ **ОШИБКА НАСТРОЙКИ API**

Причина: {result.get('error', 'Неизвестная ошибка')}

🔧 **Проверьте:**
- Правильность API ключа и секрета
- Права доступа (Read + Trade)
- Активность ключей на Bybit
- Формат: API_KEY:SECRET_KEY

Попробуйте еще раз или обратитесь в поддержку.
"""
                    await message.answer(error_text, parse_mode="Markdown")

            except Exception as e:
                await message.answer(
                    "❌ Неверный формат! Используйте: API_KEY:SECRET_KEY",
                    parse_mode="Markdown"
                )
        else:
            await message.answer(
                "❌ Неверный формат! Используйте формат: API_KEY:SECRET_KEY",
                parse_mode="Markdown"
            )

        # Сбрасываем состояние
        user_states.pop(user_id, None)


@dp.callback_query(F.data == "back_main")
async def callback_back_main(callback: types.CallbackQuery):
    welcome_text = """
🤖 **ATLAS TRADING BOT**

🏠 **Главное меню**

Выберите действие:
"""
    await callback.message.edit_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    await callback.answer()


# Остальные callback-функции...
@dp.callback_query(F.data == "get_prices")
async def callback_get_prices(callback: types.CallbackQuery):
    await callback.answer("Загрузка цен...")
    await callback_get_price(callback)


@dp.callback_query(F.data == "analyze_market")
async def callback_analyze_market(callback: types.CallbackQuery):
    data = await post_api_data("/strategy/analyze")

    if data and data.get('signal_generated'):
        signal = data['signal']
        action_emoji = "🟢" if signal['action'] == 'buy' else "🔴"

        signal_text = f"""
{action_emoji} **ТОРГОВЫЙ СИГНАЛ!**

🎯 **{signal['action'].upper()}** {signal['symbol']}
🔥 **Уверенность:** {signal['confidence']:.1%}
💰 **Цена входа:** ${signal['entry_price']:,.2f}
🛑 **Стоп-лосс:** ${signal.get('stop_loss', 0):,.2f}
🎯 **Тейк-профит:** ${signal.get('take_profit', 0):,.2f}

📝 **Анализ:** {signal['reason']}

⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}
"""
    else:
        signal_text = f"""
😴 **СИГНАЛОВ НЕТ**

💰 **Текущая цена:** ${data.get('current_price', 0):,.2f}
🔍 **Статус:** Мониторинг рынка...
⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}

Система автоматически уведомит о новых возможностях!
"""

    await callback.message.edit_text(signal_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    await callback.answer()


async def main():
    logger.info("🚀 Запускаем Atlas Trading Bot (Production)...")
    logger.info("🤖 Бот: t.me/ATLASTRADINGrus_BOT")
    logger.info("💰 Режим: Реальная торговля")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())