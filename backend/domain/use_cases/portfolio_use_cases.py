from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from ..entities.user import User, UserPortfolio, CoinTransaction, TransactionType
from ..repositories.user_repository import UserRepository, PortfolioRepository, TransactionRepository


class GetUserPortfolioUseCase:
    """Use case для получения портфеля пользователя"""
    
    def __init__(self, user_repo: UserRepository, portfolio_repo: PortfolioRepository):
        self.user_repo = user_repo
        self.portfolio_repo = portfolio_repo
    
    async def execute(self, telegram_id: int) -> Optional[List[UserPortfolio]]:
        """Получить портфель пользователя с обновленными ценами"""
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return None
        
        portfolio_items = await self.portfolio_repo.get_user_portfolio(user.id)
        
        # Обновляем текущие цены через CoinGecko API (только если есть монеты и цены устарели)
        if portfolio_items:
            try:
                from infrastructure.external_apis.coin_gecko_api import CoinGeckoAPI
                from decimal import Decimal
                from datetime import datetime, timedelta
                
                # Проверяем, нужно ли обновлять цены (если прошло более 5 минут)
                need_update = False
                for item in portfolio_items:
                    if not item.last_updated or (datetime.utcnow() - item.last_updated) > timedelta(minutes=5):
                        need_update = True
                        break
                
                if need_update:
                    print(f"Обновляем цены для {len(portfolio_items)} монет")
                    
                    coin_api = CoinGeckoAPI()
                    
                    # Получаем символы всех монет в портфеле
                    symbols = [item.symbol for item in portfolio_items]
                    print(f"Символы для обновления: {symbols}")
                    
                    # Получаем текущие цены
                    current_prices = await coin_api.get_current_prices(symbols)
                    print(f"Получены цены: {current_prices}")
                    
                    # Обновляем цены в портфеле
                    updated_count = 0
                    for item in portfolio_items:
                        symbol_lower = item.symbol.lower()
                        if symbol_lower in current_prices and current_prices[symbol_lower] > 0:
                            old_price = float(item.current_price)
                            item.current_price = Decimal(str(current_prices[symbol_lower]))
                            item.last_updated = datetime.utcnow()
                            print(f"Обновляем цену {item.symbol}: {old_price} -> {current_prices[symbol_lower]}")
                            
                            # Обновляем в базе данных
                            await self.portfolio_repo.update_portfolio_item(item)
                            updated_count += 1
                    
                    print(f"Обновлено цен в БД: {updated_count}")
                else:
                    print("Цены актуальны, обновление не требуется")
                        
            except Exception as e:
                print(f"Ошибка при обновлении цен: {e}")
                import traceback
                traceback.print_exc()
                # Продолжаем работу даже если не удалось обновить цены
        
        return portfolio_items


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
            transaction_type=TransactionType.BUY,
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


class SellCoinFromPortfolioUseCase:
    """Use case для продажи монеты из портфеля"""
    
    def __init__(self, user_repo: UserRepository, portfolio_repo: PortfolioRepository, 
                 transaction_repo: TransactionRepository):
        self.user_repo = user_repo
        self.portfolio_repo = portfolio_repo
        self.transaction_repo = transaction_repo
    
    async def execute(self, telegram_id: int, symbol: str, 
                     quantity: Decimal, price: Decimal) -> bool:
        """Продать монету из портфеля"""
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return False
        
        # Проверяем, есть ли такая монета в портфеле
        existing_coin = await self.portfolio_repo.get_portfolio_item(user.id, symbol)
        if not existing_coin:
            return False
        
        # Проверяем, достаточно ли монет для продажи
        if existing_coin.total_quantity < quantity:
            return False
        
        total_received = price * quantity
        
        # Создаем транзакцию продажи
        transaction = CoinTransaction(
            id=None,
            user_id=user.id,
            symbol=symbol,
            name=existing_coin.name,
            quantity=quantity,
            price=price,
            total_spent=total_received,  # Для продажи это сумма получена
            transaction_type=TransactionType.SELL,
            timestamp=None  # Будет установлено в репозитории
        )
        await self.transaction_repo.create_transaction(transaction)
        
        # Обновляем портфель
        new_quantity = existing_coin.total_quantity - quantity
        
        if new_quantity == 0:
            # Если продали все монеты, удаляем из портфеля
            # TODO: добавить метод delete_portfolio_item в репозиторий
            pass
        else:
            # Обновляем количество и общую потраченную сумму
            # Средняя цена остается той же
            new_total_spent = existing_coin.total_spent - (existing_coin.avg_price * quantity)
            
            updated_coin = UserPortfolio(
                id=existing_coin.id,
                user_id=user.id,
                symbol=symbol,
                name=existing_coin.name,
                total_quantity=new_quantity,
                avg_price=existing_coin.avg_price,  # Средняя цена покупки не меняется
                current_price=existing_coin.current_price,
                total_spent=new_total_spent,
                last_updated=datetime.utcnow()
            )
            await self.portfolio_repo.update_portfolio_item(updated_coin)
        
        return True 