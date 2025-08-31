from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class User:
    """Доменная сущность пользователя"""
    id: Optional[int]
    telegram_id: int
    balance: Decimal = Decimal('0')
    
    def __post_init__(self):
        if isinstance(self.balance, str):
            self.balance = Decimal(self.balance)


@dataclass
class UserPortfolio:
    """Доменная сущность портфеля пользователя"""
    id: Optional[int]
    user_id: int
    symbol: str  # Маппинг на symbol в БД
    name: str    # Маппинг на name в БД
    total_quantity: Decimal # Маппинг на total_quantity в БД
    avg_price: Decimal # Маппинг на avg_price в БД
    total_spent: Decimal
    current_price: Decimal = Decimal('0')
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.total_quantity, str):
            self.total_quantity = Decimal(self.total_quantity)
        if isinstance(self.avg_price, str):
            self.avg_price = Decimal(self.avg_price)
        if isinstance(self.current_price, str):
            self.current_price = Decimal(self.current_price)
        if isinstance(self.total_spent, str):
            self.total_spent = Decimal(self.total_spent)


@dataclass
class CoinTransaction:
    """Доменная сущность транзакции"""
    id: Optional[int]
    user_id: int
    symbol: str  # Маппинг на symbol в БД
    name: str    # Маппинг на name в БД
    quantity: Decimal
    price: Decimal
    total_spent: Decimal
    transaction_type: TransactionType = TransactionType.BUY
    timestamp: Optional[datetime] = None  # Маппинг на timestamp в БД
    
    def __post_init__(self):
        if isinstance(self.quantity, str):
            self.quantity = Decimal(self.quantity)
        if isinstance(self.price, str):
            self.price = Decimal(self.price)
        if isinstance(self.total_spent, str):
            self.total_spent = Decimal(self.total_spent) 