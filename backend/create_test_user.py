#!/usr/bin/env python3
import asyncio
from decimal import Decimal
from infrastructure.database.connection import get_async_session
from infrastructure.database.repositories import SQLAlchemyUserRepository
from domain.entities.user import User

async def create_test_user():
    async for session in get_async_session():
        try:
            repo = SQLAlchemyUserRepository(session)
            
            # Проверяем, существует ли уже пользователь с таким Telegram ID
            existing_user = await repo.get_by_telegram_id(1042267533)
            
            if existing_user:
                print(f"Пользователь с Telegram ID {1042267533} уже существует")
                print(f"ID: {existing_user.id}, Balance: {existing_user.balance}")
                return
            
            # Создаем нового пользователя
            test_user = User(
                telegram_id=1042267533,
                balance=Decimal('10000.00')
            )
            
            created_user = await repo.create(test_user)
            await session.commit()
            
            print(f"✅ Создан тестовый пользователь:")
            print(f"   ID: {created_user.id}")
            print(f"   Telegram ID: {created_user.telegram_id}")
            print(f"   Balance: {created_user.balance}")
            
            break
        except Exception as e:
            print(f"❌ Ошибка при создании пользователя: {e}")
            await session.rollback()
            break

if __name__ == "__main__":
    asyncio.run(create_test_user())




