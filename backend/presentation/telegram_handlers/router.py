from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

from domain.use_cases.portfolio_use_cases import GetUserPortfolioUseCase, AddCoinToPortfolioUseCase
from infrastructure.database.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyPortfolioRepository,
    SQLAlchemyTransactionRepository
)
from infrastructure.external_apis.coin_gecko_api import CoinGeckoAPI
from shared.config import settings

router = Router()

# Состояния FSM
class PortfolioStates(StatesGroup):
    waiting_for_symbol = State()
    waiting_for_name = State()
    waiting_for_quantity = State()
    waiting_for_price = State()

# Клавиатуры
def get_main_keyboard():
    """Получить главную клавиатуру с веб-приложением"""
    
    # URL задеплоенного фронтенда на Vercel
    webapp_url = "https://crypto-book-bot.vercel.app"
    
    keyboard = [
        [KeyboardButton(text="📊 Портфель"), KeyboardButton(text="💰 Добавить монету")],
        [KeyboardButton(text="📈 Аналитика"), KeyboardButton(text="📋 Транзакции")],
        [KeyboardButton(text="🌐 Веб-приложение", web_app=WebAppInfo(url=webapp_url))],
        [KeyboardButton(text="🔗 Получить ссылку")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "🚀 Добро пожаловать в Crypto Bot!\n\n"
        "Этот бот поможет вам отслеживать ваш криптопортфель.\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("webapp"))
async def cmd_webapp(message: Message):
    """Отправить ссылку на веб-приложение"""
    # URL задеплоенного фронтенда на Vercel
    webapp_url = "https://crypto-book-bot.vercel.app"
    
    await message.answer(
        f"🌐 Ссылка на ваше мини-приложение:\n\n"
        f"🔗 {webapp_url}\n\n"
        f"📱 Нажмите на ссылку, чтобы открыть веб-интерфейс для управления портфелем.\n\n"
        f"💡 Или используйте кнопку '🌐 Веб-приложение' в меню бота."
    )

@router.message(Command("app"))
async def cmd_app(message: Message):
    """Получить ссылку на мини-приложение"""
    import requests
    
    # Получаем ngrok URL
    # URL задеплоенного фронтенда на Vercel
    current_url = "https://crypto-book-bot.vercel.app"
    
    # Создаем инлайн клавиатуру с Web App кнопкой
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Открыть мини-приложение",
            web_app=WebAppInfo(url=current_url)
        )]
    ])
    
    await message.answer(
        f"🚀 Ваше мини-приложение готово!\n\n"
        f"📱 Нажмите кнопку ниже, чтобы открыть приложение\n"
        f"💼 Управляйте портфелем прямо в Telegram!",
        reply_markup=keyboard
    )

@router.message(Command("url"))
async def cmd_url(message: Message):
    """Получить текущий URL веб-приложения"""
    import requests
    
    # Получаем ngrok URL
    # URL задеплоенного фронтенда на Vercel
    current_url = "https://crypto-book-bot.vercel.app"
    await message.answer(
        f"🔗 Текущий URL веб-приложения:\n\n"
        f"🌐 {current_url}\n\n"
        f"📱 Используйте эту ссылку для доступа к мини-приложению."
    )

@router.message(F.text == "🌐 Веб-приложение")
async def show_webapp_info(message: Message):
    """Информация о веб-приложении"""
    await message.answer(
        "🌐 Нажмите кнопку '🌐 Веб-приложение' выше, чтобы открыть веб-интерфейс для управления вашим портфелем.\n\n"
        "В веб-приложении вы сможете:\n"
        "• Просматривать портфель в удобном формате\n"
        "• Добавлять новые монеты\n"
        "• Анализировать графики\n"
        "• Отслеживать прибыль/убытки"
    )

@router.message(F.text == "📊 Портфель")
async def show_portfolio(message: Message):
    """Показать портфель пользователя"""
    try:
        # Создаем репозитории и use case
        from infrastructure.database.connection import get_async_session
        
        async for session in get_async_session():
            user_repo = SQLAlchemyUserRepository(session)
            portfolio_repo = SQLAlchemyPortfolioRepository(session)
            
            use_case = GetUserPortfolioUseCase(user_repo, portfolio_repo)
            portfolio = await use_case.execute(message.from_user.id)
            
            if not portfolio:
                await message.answer("📭 Ваш портфель пуст. Добавьте первую монету!")
                return
            
            # Формируем сообщение с портфелем
            portfolio_text = "📊 Ваш портфель:\n\n"
            total_value = 0
            
            for item in portfolio:
                portfolio_text += f"🪙 {item.name} ({item.symbol})\n"
                portfolio_text += f"   Количество: {item.total_quantity}\n"
                portfolio_text += f"   Средняя цена: ${item.avg_price:.4f}\n"
                portfolio_text += f"   Общая стоимость: ${item.total_spent:.2f}\n\n"
                total_value += item.total_spent
            
            portfolio_text += f"💰 Общая стоимость портфеля: ${total_value:.2f}"
            
            await message.answer(portfolio_text)
            break
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении портфеля: {str(e)}")

@router.message(F.text == "💰 Добавить монету")
async def start_add_coin(message: Message, state: FSMContext):
    """Начать процесс добавления монеты"""
    await state.set_state(PortfolioStates.waiting_for_symbol)
    await message.answer(
        "🪙 Введите символ монеты (например, BTC, ETH, ADA):",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True
        )
    )

@router.message(PortfolioStates.waiting_for_symbol)
async def process_symbol(message: Message, state: FSMContext):
    """Обработка символа монеты"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Операция отменена", reply_markup=get_main_keyboard())
        return
    
    await state.update_data(symbol=message.text.upper())
    await state.set_state(PortfolioStates.waiting_for_name)
    await message.answer("📝 Введите название монеты:")

@router.message(PortfolioStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка названия монеты"""
    await state.update_data(name=message.text)
    await state.set_state(PortfolioStates.waiting_for_quantity)
    await message.answer("📊 Введите количество монет:")

@router.message(PortfolioStates.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext):
    """Обработка количества монет"""
    try:
        quantity = float(message.text)
        await state.update_data(quantity=quantity)
        await state.set_state(PortfolioStates.waiting_for_price)
        await message.answer("💵 Введите цену покупки (в USD):")
    except ValueError:
        await message.answer("❌ Введите корректное число для количества")

@router.message(PortfolioStates.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    """Обработка цены покупки"""
    try:
        price = float(message.text)
        data = await state.get_data()
        
        # Создаем транзакцию
        from infrastructure.database.connection import get_async_session
        
        async for session in get_async_session():
            user_repo = SQLAlchemyUserRepository(session)
            portfolio_repo = SQLAlchemyPortfolioRepository(session)
            transaction_repo = SQLAlchemyTransactionRepository(session)
            
            use_case = AddCoinToPortfolioUseCase(user_repo, portfolio_repo, transaction_repo)
            
            success = await use_case.execute(
                telegram_id=message.from_user.id,
                symbol=data['symbol'],
                name=data['name'],
                quantity=data['quantity'],
                price=price
            )
            
            if success:
                await message.answer(
                    f"✅ Монета {data['symbol']} успешно добавлена в портфель!",
                    reply_markup=get_main_keyboard()
                )
            else:
                await message.answer(
                    "❌ Ошибка при добавлении монеты",
                    reply_markup=get_main_keyboard()
                )
            
            await state.clear()
            break
        
    except ValueError:
        await message.answer("❌ Введите корректную цену")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=get_main_keyboard())
        await state.clear()

@router.message(F.text == "📋 Транзакции")
async def show_transactions(message: Message):
    """Показать транзакции пользователя"""
    try:
        from infrastructure.database.connection import get_async_session
        
        async for session in get_async_session():
            user_repo = SQLAlchemyUserRepository(session)
            transaction_repo = SQLAlchemyTransactionRepository(session)
            
            user = await user_repo.get_by_telegram_id(message.from_user.id)
            if not user:
                await message.answer("❌ Пользователь не найден")
                return
            
            transactions = await transaction_repo.get_user_transactions(user.id)
            
            if not transactions:
                await message.answer("📭 У вас пока нет транзакций")
                return
            
            transactions_text = "📋 Ваши транзакции:\n\n"
            
            for tx in transactions[:10]:  # Показываем последние 10
                transactions_text += f"🪙 {tx.symbol} ({tx.name})\n"
                transactions_text += f"   Количество: {tx.quantity}\n"
                transactions_text += f"   Цена: ${tx.price:.4f}\n"
                transactions_text += f"   Сумма: ${tx.total_spent:.2f}\n"
                transactions_text += f"   Дата: {tx.timestamp.strftime('%d.%m.%Y %H:%M')}\n\n"
            
            await message.answer(transactions_text)
            break
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении транзакций: {str(e)}")

@router.message(F.text == "📈 Аналитика")
async def show_analytics(message: Message):
    """Показать аналитику портфеля"""
    await message.answer(
        "📈 Аналитика портфеля\n\n"
        "Для детальной аналитики используйте веб-приложение:\n"
        "• Графики изменения цен\n"
        "• Распределение активов\n"
        "• Анализ доходности\n"
        "• Прогнозы\n\n"
        "Нажмите кнопку '🌐 Веб-приложение' для доступа к полной аналитике."
    )

@router.message(F.text == "🔗 Получить ссылку")
async def get_app_link(message: Message):
    """Получить ссылку на мини-приложение"""
    # Получаем ngrok URL
    # URL задеплоенного фронтенда на Vercel
    current_url = "https://crypto-book-bot.vercel.app"
    
    # Создаем инлайн клавиатуру с Web App кнопкой
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Открыть мини-приложение",
            web_app=WebAppInfo(url=current_url)
        )]
    ])
    
    await message.answer(
        f"🚀 Ваше мини-приложение готово!\n\n"
        f"📱 Нажмите кнопку ниже, чтобы открыть приложение\n"
        f"💼 Управляйте портфелем прямо в Telegram!",
        reply_markup=keyboard
    )

@router.message()
async def echo_message(message: Message):
    """Обработчик неизвестных сообщений"""
    await message.answer(
        "🤖 Используйте кнопки меню для навигации или отправьте /start для начала работы."
    ) 