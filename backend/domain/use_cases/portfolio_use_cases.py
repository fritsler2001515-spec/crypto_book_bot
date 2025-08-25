from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from ..entities.user import User, UserPortfolio, CoinTransaction
from ..repositories.user_repository import UserRepository, PortfolioRepository, TransactionRepository


class GetUserPortfolioUseCase:
    """Use case для получения портфеля пользователя"""
    
    def __init__(self, user_repo: UserRepository, portfolio_repo: PortfolioRepository):
        self.user_repo = user_repo
        self.portfolio_repo = portfolio_repo
    
    async def execute(self, telegram_id: int) -> Optional[List[UserPortfolio]]:
        """Получить портфель пользователя"""
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return None
        
        return await self.portfolio_repo.get_user_portfolio(user.id)


class AddCoinToPortfolioUseCase:
    """Use case для добавления монеты в портфель"""
    
    def __init__(self, user_repo: UserRepository, portfolio_repo: PortfolioRepository, 
                 transaction_repo: TransactionRepository):
        self.user_repo = user_repo
        self.portfolio_repo = portfolio_repo
        self.transaction_repo = transaction_repo
    
    async def execute(self, telegram_id: int, symbol: str, name: str, 
                     quantity: Decimal, price: Decimal) -> bool:
        """Добавить монету в портфель"""
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return False
        
        total_spent = price * quantity
        
        # Создаем транзакцию
        transaction = CoinTransaction(
            id=None,
            user_id=user.id,
            symbol=symbol,
            name=name,
            quantity=quantity,
            price=price,
            total_spent=total_spent,
            timestamp=None  # Будет установлено в репозитории
        )
        await self.transaction_repo.create_transaction(transaction)
        
        # Проверяем, есть ли уже такая монета в портфеле
        existing_coin = await self.portfolio_repo.get_portfolio_item(user.id, symbol)
        
        if existing_coin:
            # Обновляем существующую монету
            total_quantity = existing_coin.total_quantity + quantity
            total_cost = existing_coin.avg_price * existing_coin.total_quantity + total_spent
            avg_price = total_cost / total_quantity
            
            updated_coin = UserPortfolio(
                id=existing_coin.id,
                user_id=user.id,
                symbol=symbol,
                name=name,
                total_quantity=total_quantity,
                avg_price=avg_price,
                current_price=existing_coin.current_price,
                total_spent=existing_coin.total_spent + total_spent,
                last_updated=datetime.utcnow()
            )
            await self.portfolio_repo.update_portfolio_item(updated_coin)
        else:
            # Создаем новую запись в портфеле
            new_coin = UserPortfolio(
                id=None,
                user_id=user.id,
                symbol=symbol,
                name=name,
                total_quantity=quantity,
                avg_price=price,
                current_price=Decimal('0'),  # Будет обновлено позже
                total_spent=total_spent,
                last_updated=datetime.utcnow()
            )
            await self.portfolio_repo.add_coin_to_portfolio(new_coin)
        
        return True 