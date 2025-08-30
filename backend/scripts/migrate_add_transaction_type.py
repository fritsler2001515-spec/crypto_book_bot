#!/usr/bin/env python3
"""
Миграция для добавления поля transaction_type в таблицу coin_transactions
"""
import asyncio
import asyncpg
import os
from shared.config import settings

async def migrate_database():
    """Добавить поле transaction_type в существующую таблицу"""
    
    # Получаем URL базы данных
    if settings.DATABASE_URL:
        db_url = settings.DATABASE_URL
    else:
        db_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    
    print(f"Подключаемся к базе данных...")
    
    try:
        # Подключаемся к базе данных
        conn = await asyncpg.connect(db_url)
        
        # Проверяем, существует ли уже колонка
        check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'coin_transactions' 
        AND column_name = 'transaction_type';
        """
        
        existing_column = await conn.fetchval(check_column_query)
        
        if existing_column:
            print("✅ Колонка transaction_type уже существует")
        else:
            print("➕ Добавляем колонку transaction_type...")
            
            # Создаем ENUM тип, если его нет
            create_enum_query = """
            DO $$ BEGIN
                CREATE TYPE transactiontype AS ENUM ('buy', 'sell');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """
            await conn.execute(create_enum_query)
            print("✅ ENUM тип создан/проверен")
            
            # Добавляем колонку с значением по умолчанию
            add_column_query = """
            ALTER TABLE coin_transactions 
            ADD COLUMN transaction_type transactiontype NOT NULL DEFAULT 'buy';
            """
            await conn.execute(add_column_query)
            print("✅ Колонка transaction_type добавлена")
            
            # Обновляем существующие записи (все как покупки)
            update_existing_query = """
            UPDATE coin_transactions 
            SET transaction_type = 'buy' 
            WHERE transaction_type IS NULL;
            """
            updated_rows = await conn.execute(update_existing_query)
            print(f"✅ Обновлено {updated_rows} существующих записей")
        
        await conn.close()
        print("🎉 Миграция успешно завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate_database())
