import asyncio
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI
from contextlib import asynccontextmanager

from infrastructure.database.connection import init_db
from presentation.web_api.app import app as fastapi_app
from presentation.telegram_handlers.router import router as telegram_router
from shared.config import settings

# Глобальные переменные для бота
bot = None
dp = None

async def initialize_coin_cache():
    """Инициализация кэша монет при запуске"""
    try:
        from infrastructure.database.connection import AsyncSessionLocal
        from infrastructure.database.repositories import SQLAlchemyCoinCacheRepository
        from infrastructure.external_apis.coin_gecko_api import CoinGeckoAPI
        
        async with AsyncSessionLocal() as session:
            cache_repo = SQLAlchemyCoinCacheRepository(session)
            
            # Проверяем, есть ли кэш
            is_fresh = await cache_repo.is_cache_fresh('top_coins', max_age_minutes=60)
            
            if not is_fresh:
                print("🔄 Инициализация кэша топ монет...")
                try:
                    async with CoinGeckoAPI() as api:
                        coins = await asyncio.wait_for(api.get_top_coins(100), timeout=20.0)
                        if coins:
                            await cache_repo.update_cache(coins, 'top_coins')
                            print(f"✅ Кэш топ монет инициализирован ({len(coins)} монет)")
                        else:
                            print("⚠️ Не удалось получить данные от CoinGecko API")
                except asyncio.TimeoutError:
                    print("⏱️ Timeout при инициализации кэша топ монет")
                except Exception as e:
                    print(f"❌ Ошибка при инициализации кэша топ монет: {e}")
                
                # Инициализация лидеров роста
                print("🔄 Инициализация кэша лидеров роста...")
                try:
                    async with CoinGeckoAPI() as api:
                        coins = await asyncio.wait_for(api.get_growth_leaders(20), timeout=20.0)
                        if coins:
                            await cache_repo.update_cache(coins, 'growth_leaders')
                            print(f"✅ Кэш лидеров роста инициализирован ({len(coins)} монет)")
                except asyncio.TimeoutError:
                    print("⏱️ Timeout при инициализации кэша лидеров роста")
                except Exception as e:
                    print(f"❌ Ошибка при инициализации кэша лидеров роста: {e}")
            else:
                print("✅ Кэш монет уже актуален")
                
    except Exception as e:
        print(f"❌ Критическая ошибка при инициализации кэша: {e}")
        import traceback
        traceback.print_exc()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot, dp
    
    # Инициализация базы данных
    init_db()
    print("✅ База данных инициализирована")
    
    # Инициализация кэша монет
    await initialize_coin_cache()
    
    # Создание и настройка бота (только если токен валидный)
    if settings.BOT_TOKEN and settings.BOT_TOKEN != "your_telegram_bot_token_here":
        try:
            bot = Bot(token=settings.BOT_TOKEN)
            dp = Dispatcher(storage=MemoryStorage())
            dp.include_router(telegram_router)
            
            # Запуск бота в фоновом режиме
            asyncio.create_task(dp.start_polling(bot))
            print("✅ Telegram бот запущен")
        except Exception as e:
            print(f"⚠️ Telegram бот не запущен: {e}")
            print("📱 Работает только веб-версия")
    else:
        print("📱 Telegram бот отключен - работает только веб-версия")
    
    yield
    
    # Очистка при остановке
    if bot:
        await bot.session.close()
    print("✅ Приложение остановлено")

app = FastAPI(
    title="Crypto Bot API",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS для решения проблем с фронтендом
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Разрешаем все домены для упрощения
        "https://crypto-book-bot.vercel.app",  # Frontend
        "https://web.telegram.org",  # Telegram Web App
        "https://telegram.org",  # Telegram
    ],
    allow_credentials=False,  # Отключаем credentials для упрощения
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "*",
        "Content-Type",
        "Authorization", 
        "X-Requested-With",
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Mx-ReqToken",
        "Keep-Alive",
        "If-Modified-Since",
    ],
)

# Подключаем роутер напрямую
from presentation.web_api.app import api_router
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", settings.API_PORT))  # Railway использует PORT
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Слушаем все интерфейсы
        port=port,
        reload=False,  # Отключаем reload для production
        proxy_headers=True,
        forwarded_allow_ips="*",
        access_log=True,
        server_header=False  # Отключаем проверку заголовка Host
    ) 