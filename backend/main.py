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

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot, dp
    
    # Инициализация базы данных
    init_db()
    print("✅ База данных инициализирована")
    
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