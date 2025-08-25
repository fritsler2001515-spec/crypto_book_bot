from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from shared.config import settings

# Синхронное подключение (для миграций)
engine = create_engine(settings.DB_URL)
Session = sessionmaker(bind=engine)

# Асинхронное подключение (для приложения)
async_engine = create_async_engine(settings.ASYNC_DB_URL)
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

def get_session():
    """Получить синхронную сессию"""
    return Session()

async def get_async_session():
    """Получить асинхронную сессию"""
    async with AsyncSessionLocal() as session:
        yield session

def init_db():
    """Инициализация базы данных"""
    from .models import Base
    Base.metadata.create_all(engine) 