from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, BigInteger, TIMESTAMP, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    balance = Column(Numeric, default=0)

    portfolio = relationship("UserPortfolio", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("CoinTransaction", back_populates="user", cascade="all, delete-orphan")


class UserPortfolio(Base):
    __tablename__ = 'user_portfolio'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    symbol = Column(String, nullable=False)  # Используем старые названия полей
    name = Column(String, nullable=False)    # для совместимости с существующей БД
    total_quantity = Column(Numeric, nullable=False)
    avg_price = Column(Numeric, nullable=False)
    current_price = Column(Numeric, default=0)
    total_spent = Column(Numeric, nullable=False)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="portfolio")


class CoinTransaction(Base):
    __tablename__ = 'coin_transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    symbol = Column(String, nullable=False)  # Используем старые названия полей
    name = Column(String, nullable=False)    # для совместимости с существующей БД
    quantity = Column(Numeric, nullable=False)
    price = Column(Numeric, nullable=False)
    total_spent = Column(Numeric, nullable=False)
    transaction_type = Column(String, nullable=True, default="BUY")
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


class CoinCache(Base):
    """Кэш для топ монет"""
    __tablename__ = 'coin_cache'

    id = Column(String, primary_key=True)  # coin_id из CoinGecko
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=True)
    market_cap_rank = Column(Integer, nullable=True)
    price_change_percentage_24h = Column(Float, nullable=True)
    image = Column(String, nullable=True)
    total_volume = Column(Float, nullable=True)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    cache_type = Column(String, default='top_coins')  # 'top_coins' или 'growth_leaders' 