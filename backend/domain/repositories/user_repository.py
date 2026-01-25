from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.user import User, UserPortfolio, CoinTransaction


class UserRepository(ABC):
    """Интерфейс репозитория для работы с пользователями"""
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Создать нового пользователя"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        pass


class PortfolioRepository(ABC):
    """Интерфейс репозитория для работы с портфелем"""
    
    @abstractmethod
    async def get_user_portfolio(self, user_id: int) -> List[UserPortfolio]:
        """Получить портфель пользователя"""
        pass
    
    @abstractmethod
    async def add_coin_to_portfolio(self, portfolio_item: UserPortfolio) -> UserPortfolio:
        """Добавить монету в портфель"""
        pass
    
    @abstractmethod
    async def update_portfolio_item(self, portfolio_item: UserPortfolio) -> UserPortfolio:
        """Обновить элемент портфеля"""
        pass
    
    @abstractmethod
    async def get_portfolio_item(self, user_id: int, symbol: str) -> Optional[UserPortfolio]:
        """Получить конкретную монету из портфеля"""
        pass

    @abstractmethod
    async def delete_portfolio_item(self, portfolio_item_id: int) -> bool:
        """Удалить элемент из портфеля"""
        pass


class TransactionRepository(ABC):
    """Интерфейс репозитория для работы с транзакциями"""
    
    @abstractmethod
    async def create_transaction(self, transaction: CoinTransaction) -> CoinTransaction:
        """Создать новую транзакцию"""
        pass
    
    @abstractmethod
    async def get_user_transactions(self, user_id: int) -> List[CoinTransaction]:
        """Получить все транзакции пользователя"""
        pass 