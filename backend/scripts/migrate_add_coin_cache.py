"""
Миграция для добавления таблицы coin_cache
"""
import asyncio
import asyncpg
from shared.config import settings


async def migrate():
    """Создать таблицу coin_cache"""
    try:
        # Получаем URL базы данных
        if settings.DATABASE_URL:
            db_url = settings.DATABASE_URL
        else:
            db_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        
        print("🔄 Начинаем миграцию: создание таблицы coin_cache...")
        
        # Подключаемся к базе данных
        conn = await asyncpg.connect(db_url)
        
        # Проверяем, существует ли таблица
        check_table_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'coin_cache'
        );
        """
        
        table_exists = await conn.fetchval(check_table_query)
        
        if table_exists:
            print("✅ Таблица coin_cache уже существует")
            await conn.close()
            return
        
        # Создаем таблицу
        create_table_query = """
        CREATE TABLE coin_cache (
            id VARCHAR PRIMARY KEY,
            symbol VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            current_price DOUBLE PRECISION NOT NULL,
            market_cap DOUBLE PRECISION,
            market_cap_rank INTEGER,
            price_change_percentage_24h DOUBLE PRECISION,
            image VARCHAR,
            total_volume DOUBLE PRECISION,
            last_updated TIMESTAMP DEFAULT NOW(),
            cache_type VARCHAR DEFAULT 'top_coins'
        );
        """
        
        await conn.execute(create_table_query)
        print("✅ Таблица coin_cache создана")
        
        # Создаем индексы для быстрого поиска
        create_index_query = """
        CREATE INDEX idx_coin_cache_type ON coin_cache(cache_type);
        CREATE INDEX idx_coin_cache_rank ON coin_cache(market_cap_rank);
        """
        
        await conn.execute(create_index_query)
        print("✅ Индексы созданы")
        
        await conn.close()
        print("✅ Миграция успешно завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(migrate())
