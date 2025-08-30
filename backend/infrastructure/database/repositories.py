from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
from datetime import datetime

from domain.entities.user import User as UserEntity, UserPortfolio as PortfolioEntity, CoinTransaction as TransactionEntity, TransactionType
from domain.repositories.user_repository import UserRepository, PortfolioRepository, TransactionRepository
from .models import User, UserPortfolio, CoinTransaction, TransactionType as DBTransactionType

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[UserEntity]:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user:
            return UserEntity(
                id=user.id,
                telegram_id=user.telegram_id,
                balance=user.balance
            )
        return None

    async def create(self, user: UserEntity) -> UserEntity:
        db_user = User(
            telegram_id=user.telegram_id,
            balance=user.balance
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return UserEntity(
            id=db_user.id,
            telegram_id=db_user.telegram_id,
            balance=db_user.balance
        )

    async def update(self, user: UserEntity) -> UserEntity:
        result = await self.session.execute(
            select(User).where(User.id == user.id)
        )
        db_user = result.scalar_one_or_none()
        if db_user:
            db_user.balance = user.balance
            await self.session.commit()
            await self.session.refresh(db_user)
            return UserEntity(
                id=db_user.id,
                telegram_id=db_user.telegram_id,
                balance=db_user.balance
            )
        return user

class SQLAlchemyPortfolioRepository(PortfolioRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_portfolio(self, user_id: int) -> List[PortfolioEntity]:
        result = await self.session.execute(
            select(UserPortfolio).where(UserPortfolio.user_id == user_id)
        )
        portfolio_items = result.scalars().all()
        return [
            PortfolioEntity(
                id=item.id,
                user_id=item.user_id,
                symbol=item.symbol,
                name=item.name,
                total_quantity=item.total_quantity,
                avg_price=item.avg_price,
                current_price=item.current_price or Decimal('0'),
                total_spent=item.total_spent,
                last_updated=item.last_updated
            )
            for item in portfolio_items
        ]

    async def create_portfolio_item(self, portfolio_item: PortfolioEntity) -> PortfolioEntity:
        db_item = UserPortfolio(
            user_id=portfolio_item.user_id,
            symbol=portfolio_item.symbol,
            name=portfolio_item.name,
            total_quantity=portfolio_item.total_quantity,
            avg_price=portfolio_item.avg_price,
            current_price=portfolio_item.current_price,
            total_spent=portfolio_item.total_spent,
            last_updated=portfolio_item.last_updated or datetime.utcnow()
        )
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return PortfolioEntity(
            id=db_item.id,
            user_id=db_item.user_id,
            symbol=db_item.symbol,
            name=db_item.name,
            total_quantity=db_item.total_quantity,
            avg_price=db_item.avg_price,
            current_price=db_item.current_price,
            total_spent=db_item.total_spent,
            last_updated=db_item.last_updated
        )

    async def update_portfolio_item(self, portfolio_item: PortfolioEntity) -> PortfolioEntity:
        result = await self.session.execute(
            select(UserPortfolio).where(UserPortfolio.id == portfolio_item.id)
        )
        db_item = result.scalar_one_or_none()
        if db_item:
            db_item.total_quantity = portfolio_item.total_quantity
            db_item.avg_price = portfolio_item.avg_price
            db_item.current_price = portfolio_item.current_price
            db_item.total_spent = portfolio_item.total_spent
            db_item.last_updated = portfolio_item.last_updated or datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(db_item)
            return PortfolioEntity(
                id=db_item.id,
                user_id=db_item.user_id,
                symbol=db_item.symbol,
                name=db_item.name,
                total_quantity=db_item.total_quantity,
                avg_price=db_item.avg_price,
                current_price=db_item.current_price,
                total_spent=db_item.total_spent,
                last_updated=db_item.last_updated
            )
        return portfolio_item

    async def get_by_symbol(self, user_id: int, coin_symbol: str) -> Optional[PortfolioEntity]:
        result = await self.session.execute(
            select(UserPortfolio).where(
                UserPortfolio.user_id == user_id,
                UserPortfolio.symbol == coin_symbol
            )
        )
        item = result.scalar_one_or_none()
        if item:
            return PortfolioEntity(
                id=item.id,
                user_id=item.user_id,
                symbol=item.symbol,
                name=item.name,
                total_quantity=item.total_quantity,
                avg_price=item.avg_price,
                current_price=item.current_price or Decimal('0'),
                total_spent=item.total_spent,
                last_updated=item.last_updated
            )
        return None

    async def add_coin_to_portfolio(self, portfolio_item: PortfolioEntity) -> PortfolioEntity:
        """Добавить монету в портфель (алиас для create_portfolio_item)"""
        return await self.create_portfolio_item(portfolio_item)

    async def get_portfolio_item(self, user_id: int, symbol: str) -> Optional[PortfolioEntity]:
        """Получить конкретную монету из портфеля (алиас для get_by_symbol)"""
        return await self.get_by_symbol(user_id, symbol)

class SQLAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(self, transaction: TransactionEntity) -> TransactionEntity:
        # Преобразуем доменный тип в тип БД
        db_transaction_type = DBTransactionType.BUY if transaction.transaction_type == TransactionType.BUY else DBTransactionType.SELL
        
        # Создаем транзакцию с обработкой случая, когда колонка может не существовать
        transaction_data = {
            'user_id': transaction.user_id,
            'symbol': transaction.symbol,
            'name': transaction.name,
            'quantity': transaction.quantity,
            'price': transaction.price,
            'total_spent': transaction.total_spent,
            'timestamp': transaction.timestamp or datetime.utcnow()
        }
        
        # Добавляем transaction_type только если колонка существует
        try:
            transaction_data['transaction_type'] = db_transaction_type
            db_transaction = CoinTransaction(**transaction_data)
        except Exception as e:
            print(f"Создаем транзакцию без типа (старая схема БД): {e}")
            # Убираем transaction_type для совместимости со старой схемой
            del transaction_data['transaction_type']
            db_transaction = CoinTransaction(**transaction_data)
        self.session.add(db_transaction)
        await self.session.commit()
        await self.session.refresh(db_transaction)
        # Преобразуем тип БД обратно в доменный тип
        domain_transaction_type = TransactionType.BUY
        if hasattr(db_transaction, 'transaction_type') and db_transaction.transaction_type:
            domain_transaction_type = TransactionType.BUY if db_transaction.transaction_type == DBTransactionType.BUY else TransactionType.SELL
        
        return TransactionEntity(
            id=db_transaction.id,
            user_id=db_transaction.user_id,
            symbol=db_transaction.symbol,
            name=db_transaction.name,
            quantity=db_transaction.quantity,
            price=db_transaction.price,
            total_spent=db_transaction.total_spent,
            transaction_type=domain_transaction_type,
            timestamp=db_transaction.timestamp
        )

    async def get_user_transactions(self, user_id: int) -> List[TransactionEntity]:
        # Проверяем, существует ли колонка transaction_type
        try:
            # Пытаемся выполнить запрос с transaction_type
            result = await self.session.execute(
                select(CoinTransaction).where(CoinTransaction.user_id == user_id)
                .order_by(CoinTransaction.timestamp.desc())
            )
            transactions = result.scalars().all()
            return [
                TransactionEntity(
                    id=tx.id,
                    user_id=tx.user_id,
                    symbol=tx.symbol,
                    name=tx.name,
                    quantity=tx.quantity,
                    price=tx.price,
                    total_spent=tx.total_spent,
                    transaction_type=TransactionType.SELL if (hasattr(tx, 'transaction_type') and tx.transaction_type == DBTransactionType.SELL) else TransactionType.BUY,
                    timestamp=tx.timestamp
                )
                for tx in transactions
            ]
        except Exception as e:
            if "transaction_type does not exist" in str(e):
                print("Колонка transaction_type не существует, используем старую схему")
                # Выполняем запрос без transaction_type
                result = await self.session.execute(
                    select(CoinTransaction.id, CoinTransaction.user_id, CoinTransaction.symbol, 
                          CoinTransaction.name, CoinTransaction.quantity, CoinTransaction.price,
                          CoinTransaction.total_spent, CoinTransaction.timestamp)
                    .where(CoinTransaction.user_id == user_id)
                    .order_by(CoinTransaction.timestamp.desc())
                )
                transactions = result.all()
                return [
                    TransactionEntity(
                        id=tx.id,
                        user_id=tx.user_id,
                        symbol=tx.symbol,
                        name=tx.name,
                        quantity=tx.quantity,
                        price=tx.price,
                        total_spent=tx.total_spent,
                        transaction_type=TransactionType.BUY,  # Все старые транзакции считаем покупками
                        timestamp=tx.timestamp
                    )
                    for tx in transactions
                ]
            else:
                raise 