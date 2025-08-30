from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class ErrorResponse(BaseModel):
    """Схема ответа для ошибок"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserResponse(BaseModel):
    """Схема ответа для пользователя"""
    id: int
    telegram_id: int
    balance: Decimal
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v)
        }
    )


class PortfolioItemResponse(BaseModel):
    """Схема элемента портфеля"""
    id: int
    user_id: int
    symbol: str
    name: str
    total_quantity: float
    avg_price: float
    current_price: float
    total_spent: float
    last_updated: datetime


class PortfolioResponse(BaseModel):
    """Схема ответа для портфеля"""
    telegram_id: int
    portfolio: List[PortfolioItemResponse]


class TransactionResponse(BaseModel):
    """Схема ответа для транзакции"""
    id: Optional[int] = None
    symbol: str
    name: str
    quantity: Decimal
    price: Decimal
    total_spent: Optional[Decimal] = None
    transaction_type: TransactionType = TransactionType.BUY
    timestamp: Optional[datetime] = None
    total_amount: Optional[Decimal] = None
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v)
        }
    )


class AddCoinRequest(BaseModel):
    """Схема запроса для добавления монеты"""
    telegram_id: int
    symbol: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)


class SellCoinRequest(BaseModel):
    """Схема запроса для продажи монеты"""
    telegram_id: int
    symbol: str = Field(..., min_length=1, max_length=10)
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v)
        }
    )


class PriceResponse(BaseModel):
    """Схема ответа для цены"""
    symbol: str
    name: str
    price: Decimal
    currency: str = "USD"
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v)
        }
    )


class CoinDataResponse(BaseModel):
    """Схема ответа для данных о криптовалюте"""
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: Optional[float] = None
    market_cap_rank: Optional[int] = None
    price_change_percentage_24h: Optional[float] = None
    image: Optional[str] = None
    total_volume: Optional[float] = None
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v)
        }
    )


 