from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal
from datetime import datetime

from infrastructure.database.connection import get_async_session
from infrastructure.database.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyPortfolioRepository,
    SQLAlchemyTransactionRepository
)
from domain.use_cases.portfolio_use_cases import GetUserPortfolioUseCase, AddCoinToPortfolioUseCase
from domain.entities.user import UserPortfolio, CoinTransaction
from infrastructure.external_apis.coin_gecko_api import CoinGeckoAPI
from shared.types.api_schemas import (
    PortfolioResponse,
    PortfolioItemResponse,
    AddCoinRequest,
    TransactionResponse,
    UserResponse,
    CoinDataResponse,
    ErrorResponse
)

app = FastAPI(title="Crypto Bot API", version="1.0.0")

# Создаем подприложение для API без префикса (он добавляется в main.py)
api_router = APIRouter()

# Подключаем API роутер
app.include_router(api_router)

# Настройка CORS для решения проблем с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Разрешаем все домены для упрощения
        "https://crypto-book-bot.vercel.app",  # Frontend
        "https://web.telegram.org",  # Telegram Web App
        "https://telegram.org",  # Telegram
    ],
    allow_credentials=False,  # Отключаем credentials для упрощения
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "*",
        "Content-Type",
        "Authorization", 
        "X-Requested-With",
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Mx-ReqToken",
        "Keep-Alive",
        "X-Requested-With",
        "If-Modified-Since",
    ],
)

@api_router.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@api_router.get("/status")
async def api_status():
    """Проверка статуса API"""
    return {"status": "success", "server": "CryptoBot Backend", "version": "1.0.0", "uptime": "running"}

@api_router.get("/test")
async def test_endpoint():
    """Тестовый эндпоинт"""
    return {"message": "API router работает!"}

@api_router.get("/portfolio-test/{telegram_id}")
async def test_portfolio(telegram_id: int):
    """Тестовый эндпоинт портфеля"""
    data = {
        "telegram_id": telegram_id,
        "portfolio": [
            {
                "id": 1,
                "symbol": "BTC", 
                "name": "Bitcoin",
                "total_quantity": 1.0,
                "current_price": 50000.0
            }
        ]
    }
    
    response = JSONResponse(content=data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Dependency injection functions
async def get_user_repository(session: AsyncSession = Depends(get_async_session)):
    return SQLAlchemyUserRepository(session)

async def get_portfolio_repository(session: AsyncSession = Depends(get_async_session)):
    return SQLAlchemyPortfolioRepository(session)

async def get_transaction_repository(session: AsyncSession = Depends(get_async_session)):
    return SQLAlchemyTransactionRepository(session)

# API Endpoints
@api_router.get("/users/{telegram_id}", response_model=UserResponse)
async def get_user(
    telegram_id: int,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)
):
    """Получить пользователя по Telegram ID"""
    try:
        user = await user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            balance=user.balance
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")





@api_router.get("/portfolio/{telegram_id}")
async def get_portfolio(
    telegram_id: int, 
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    portfolio_repo: SQLAlchemyPortfolioRepository = Depends(get_portfolio_repository)
):
    """Получить портфель пользователя с текущими ценами"""
    
    try:
        # Используем use case для получения реальных данных
        use_case = GetUserPortfolioUseCase(user_repo, portfolio_repo)
        portfolio_items = await use_case.execute(telegram_id)
        
        if not portfolio_items:
            # Если портфель пустой, возвращаем пустую структуру
            return {
                "telegram_id": telegram_id,
                "portfolio": []
            }
        
        # Преобразуем данные портфеля в нужный формат
        portfolio_data = []
        for item in portfolio_items:
            portfolio_data.append({
                "id": item.id,
                "user_id": item.user_id,
                "symbol": item.symbol,
                "name": item.name,
                "total_quantity": float(item.total_quantity),
                "avg_price": float(item.avg_price),
                "current_price": float(item.current_price) if item.current_price else 0.0,
                "total_spent": float(item.total_spent),
                "last_updated": item.last_updated.isoformat() if item.last_updated else None
            })
        
        return {
            "telegram_id": telegram_id,
            "portfolio": portfolio_data
        }
        
    except Exception as e:
        print(f"Ошибка при получении портфеля: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении портфеля: {str(e)}")

@api_router.post("/portfolio/add-coin", response_model=TransactionResponse)
async def add_coin_to_portfolio(
    request: AddCoinRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    portfolio_repo: SQLAlchemyPortfolioRepository = Depends(get_portfolio_repository),
    transaction_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository)
):
    """Добавить монету в портфель"""
    
    try:
        # Логируем запрос для отладки
        print(f"Получен запрос на добавление монеты: {request}")
        
        # Проверяем, существует ли пользователь, если нет - создаем
        user = await user_repo.get_by_telegram_id(request.telegram_id)
        if not user:
            print(f"Создаем нового пользователя с telegram_id: {request.telegram_id}")
            from domain.entities.user import User
            from decimal import Decimal
            new_user = User(
                telegram_id=request.telegram_id,
                balance=Decimal('10000.00')
            )
            user = await user_repo.create(new_user)
            print(f"Создан пользователь с ID: {user.id}")
        
        use_case = AddCoinToPortfolioUseCase(user_repo, portfolio_repo, transaction_repo)
        
        success = await use_case.execute(
            telegram_id=request.telegram_id,
            symbol=request.symbol,
            name=request.name,
            quantity=request.quantity,
            price=request.price
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Ошибка при добавлении монеты")
        
        return TransactionResponse(
            symbol=request.symbol,
            name=request.name,
            quantity=request.quantity,
            price=request.price,
            total_amount=request.quantity * request.price
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка в add_coin_to_portfolio: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении монеты: {str(e)}")

@api_router.get("/transactions/{telegram_id}", response_model=List[TransactionResponse])
async def get_transactions(
    telegram_id: int,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    transaction_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository)
):
    """Получить транзакции пользователя"""
    
    try:
        user = await user_repo.get_by_telegram_id(telegram_id)
        if not user:
            # Если пользователя нет, возвращаем пустой список вместо 404
            return []
        
        transactions = await transaction_repo.get_user_transactions(user.id)
        return [
            TransactionResponse(
                id=tx.id,
                symbol=tx.symbol,
                name=tx.name,
                quantity=tx.quantity,
                price=tx.price,
                total_spent=tx.total_spent,
                timestamp=tx.timestamp
            )
            for tx in transactions
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении транзакций: {str(e)}")

@api_router.get("/market/top-coins", response_model=List[CoinDataResponse])
async def get_top_coins(limit: int = 10, response: Response = None):
    """Получить топ монет по рыночной капитализации"""
    
    # Добавляем CORS заголовки
    if response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    try:
        async with CoinGeckoAPI() as api:
            coins = await api.get_top_coins(limit)
            if coins:
                return [
                    CoinDataResponse(
                        id=coin['id'],
                        symbol=coin['symbol'],
                        name=coin['name'],
                        current_price=coin['current_price'],
                        market_cap=coin['market_cap'],
                        market_cap_rank=coin['market_cap_rank'],
                        price_change_percentage_24h=coin['price_change_percentage_24h'],
                        image=coin['image'],
                        total_volume=coin['total_volume']
                    )
                    for coin in coins
                ]
    except Exception as e:
        print(f"Ошибка при получении топ монет: {e}")
    
    # Fallback: возвращаем тестовые данные если API недоступен
    return [
        CoinDataResponse(
            id="bitcoin",
            symbol="BTC",
            name="Bitcoin",
            current_price=112000.0,
            market_cap=2200000000000.0,
            market_cap_rank=1,
            price_change_percentage_24h=-1.5,
            image="https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png",
            total_volume=50000000000.0
        ),
        CoinDataResponse(
            id="ethereum",
            symbol="ETH",
            name="Ethereum",
            current_price=4600.0,
            market_cap=550000000000.0,
            market_cap_rank=2,
            price_change_percentage_24h=-2.1,
            image="https://coin-images.coingecko.com/coins/images/279/large/ethereum.png",
            total_volume=30000000000.0
        )
    ][:limit]

@api_router.get("/market/growth-leaders", response_model=List[CoinDataResponse])
async def get_growth_leaders(limit: int = 5, response: Response = None):
    """Получить лидеров роста за 24 часа"""
    
    # Добавляем CORS заголовки
    if response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    try:
        async with CoinGeckoAPI() as api:
            coins = await api.get_growth_leaders(limit)
            if coins:
                return [
                    CoinDataResponse(
                        id=coin['id'],
                        symbol=coin['symbol'],
                        name=coin['name'],
                        current_price=coin['current_price'],
                        market_cap=coin['market_cap'],
                        market_cap_rank=coin['market_cap_rank'],
                        price_change_percentage_24h=coin['price_change_percentage_24h'],
                        image=coin['image'],
                        total_volume=coin['total_volume']
                    )
                    for coin in coins
                ]
    except Exception as e:
        print(f"Ошибка при получении лидеров роста: {e}")
    
    # Fallback: возвращаем тестовые данные лидеров роста
    return [
        CoinDataResponse(
            id="hyperliquid",
            symbol="HYPE",
            name="Hyperliquid",
            current_price=46.0,
            market_cap=15000000000.0,
            market_cap_rank=14,
            price_change_percentage_24h=4.5,
            image="https://coin-images.coingecko.com/coins/images/50882/large/hyperliquid.jpg",
            total_volume=500000000.0
        ),
        CoinDataResponse(
            id="example-coin",
            symbol="EXM",
            name="Example Coin",
            current_price=1.25,
            market_cap=1000000000.0,
            market_cap_rank=150,
            price_change_percentage_24h=3.2,
            image="https://via.placeholder.com/64",
            total_volume=50000000.0
        )
    ][:limit]

@api_router.get("/prices/{coin_names}")
async def get_current_prices(coin_names: str):
    """Получить текущие цены для списка монет"""
    try:
        # Разделяем имена монет по запятой
        names = [name.strip() for name in coin_names.split(',') if name.strip()]
        
        if not names:
            raise HTTPException(status_code=400, detail="Не указаны имена монет")
        
        async with CoinGeckoAPI() as api:
            prices = await api.get_prices_batch(names)
            
            # Преобразуем Decimal в float для JSON сериализации
            return {
                "prices": {name: float(price) for name, price in prices.items()},
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении цен: {str(e)}")


 