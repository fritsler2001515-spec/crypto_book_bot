import pytest
from decimal import Decimal
from datetime import datetime

from domain.entities.user import User, UserPortfolio, CoinTransaction


class TestUserEntity:
    """Тесты для доменной сущности User"""
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User(
            id=1,
            telegram_id=123456789,
            balance=Decimal('1000.50')
        )
        
        assert user.id == 1
        assert user.telegram_id == 123456789
        assert user.balance == Decimal('1000.50')
    
    def test_user_balance_conversion(self):
        """Тест конвертации баланса из строки"""
        user = User(
            id=1,
            telegram_id=123456789,
            balance='1000.50'
        )
        
        assert user.balance == Decimal('1000.50')


class TestUserPortfolioEntity:
    """Тесты для доменной сущности UserPortfolio"""
    
    def test_portfolio_creation(self):
        """Тест создания портфеля"""
        portfolio = UserPortfolio(
            id=1,
            user_id=1,
            symbol='BTC',
            name='Bitcoin',
            total_quantity=Decimal('1.5'),
            avg_price=Decimal('50000.00'),
            current_price=Decimal('55000.00'),
            total_spent=Decimal('75000.00'),
            last_updated=datetime.utcnow()
        )
        
        assert portfolio.symbol == 'BTC'
        assert portfolio.name == 'Bitcoin'
        assert portfolio.total_quantity == Decimal('1.5')
        assert portfolio.avg_price == Decimal('50000.00')
    
    def test_portfolio_string_conversion(self):
        """Тест конвертации строковых значений"""
        portfolio = UserPortfolio(
            id=1,
            user_id=1,
            symbol='ETH',
            name='Ethereum',
            total_quantity='2.0',
            avg_price='3000.00',
            current_price='3200.00',
            total_spent='6000.00',
            last_updated=datetime.utcnow()
        )
        
        assert portfolio.total_quantity == Decimal('2.0')
        assert portfolio.avg_price == Decimal('3000.00')


class TestCoinTransactionEntity:
    """Тесты для доменной сущности CoinTransaction"""
    
    def test_transaction_creation(self):
        """Тест создания транзакции"""
        transaction = CoinTransaction(
            id=1,
            user_id=1,
            symbol='BTC',
            name='Bitcoin',
            quantity=Decimal('0.5'),
            price=Decimal('50000.00'),
            total_spent=Decimal('25000.00'),
            timestamp=datetime.utcnow()
        )
        
        assert transaction.symbol == 'BTC'
        assert transaction.quantity == Decimal('0.5')
        assert transaction.price == Decimal('50000.00')
        assert transaction.total_spent == Decimal('25000.00') 