#!/usr/bin/env python3
"""
Скрипт для инициализации и проверки базы данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from infrastructure.database.models import Base, User, UserPortfolio, CoinTransaction
from shared.config import settings


def check_database_connection():
    """Проверка подключения к базе данных"""
    try:
        engine = create_engine(settings.DB_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Подключение к базе данных успешно")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False


def check_tables():
    """Проверка существования таблиц"""
    try:
        engine = create_engine(settings.DB_URL)
        with engine.connect() as conn:
            # Проверяем существование таблиц
            tables = ['users', 'user_portfolio', 'coin_transactions']
            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"✅ Таблица {table}: {count} записей")
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки таблиц: {e}")
        return False


def test_data_operations():
    """Тестирование операций с данными"""
    try:
        engine = create_engine(settings.DB_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Тест создания пользователя
        test_user = User(
            telegram_id=123456789,
            balance=1000.0
        )
        session.add(test_user)
        session.commit()
        print("✅ Тест создания пользователя прошел")
        
        # Тест создания портфеля
        test_portfolio = UserPortfolio(
            user_id=test_user.id,
            symbol="BTC",
            name="Bitcoin",
            total_quantity=0.5,
            avg_price=50000.0,
            current_price=55000.0,
            total_spent=25000.0
        )
        session.add(test_portfolio)
        session.commit()
        print("✅ Тест создания портфеля прошел")
        
        # Тест создания транзакции
        test_transaction = CoinTransaction(
            user_id=test_user.id,
            symbol="BTC",
            name="Bitcoin",
            quantity=0.1,
            price=50000.0,
            total_spent=5000.0
        )
        session.add(test_transaction)
        session.commit()
        print("✅ Тест создания транзакции прошел")
        
        # Очистка тестовых данных
        session.delete(test_transaction)
        session.delete(test_portfolio)
        session.delete(test_user)
        session.commit()
        print("✅ Тестовые данные очищены")
        
        session.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка тестирования операций: {e}")
        return False


def main():
    """Основная функция"""
    print("🔍 Проверка базы данных...")
    print(f"📊 URL базы данных: {settings.DB_URL}")
    
    # Проверка подключения
    if not check_database_connection():
        return
    
    # Проверка таблиц
    if not check_tables():
        return
    
    # Тестирование операций
    if not test_data_operations():
        return
    
    print("🎉 Все проверки пройдены успешно!")


if __name__ == "__main__":
    main() 