from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal
from datetime import datetime

from infrastructure.database.connection import get_async_session
from infrastructure.database.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyPortfolioRepository,
    SQLAlchemyTransactionRepository,
    SQLAlchemyCoinCacheRepository
)
from domain.use_cases.portfolio_use_cases import GetUserPortfolioUseCase, AddCoinToPortfolioUseCase, SellCoinFromPortfolioUseCase
from domain.entities.user import UserPortfolio, CoinTransaction, TransactionType
from infrastructure.external_apis.coin_gecko_api import CoinGeckoAPI
from shared.types.api_schemas import (
    PortfolioResponse,
    PortfolioItemResponse,
    AddCoinRequest,
    SellCoinRequest,
    TransactionResponse,
    UserResponse,
    CoinDataResponse,
    ErrorResponse,
    TransactionType as APITransactionType
)

app = FastAPI(title="Crypto Bot API", version="1.0.0")

# Создаем подприложение для API без префикса (он добавляется в main.py)
api_router = APIRouter()

# Подключаем API роутер
app.include_router(api_router)

# CORS middleware перенесен в main.py

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

@api_router.post("/admin/migrate-transaction-type")
async def migrate_transaction_type():
    """Миграция для добавления поля transaction_type"""
    try:
        import asyncpg
        from shared.config import settings
        
        # Получаем URL базы данных
        if settings.DATABASE_URL:
            db_url = settings.DATABASE_URL
        else:
            db_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        
        print("Начинаем миграцию базы данных...")
        
        # Подключаемся к базе данных
        conn = await asyncpg.connect(db_url)
        
        # Проверяем, существует ли уже колонка
        check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'coin_transactions' 
        AND column_name = 'transaction_type';
        """
        
        existing_column = await conn.fetchval(check_column_query)
        
        if existing_column:
            await conn.close()
            return {"status": "success", "message": "Колонка transaction_type уже существует"}
        
        print("Добавляем колонку transaction_type...")
        
        # Сначала добавляем колонку как TEXT
        try:
            add_column_query = """
            ALTER TABLE coin_transactions 
            ADD COLUMN transaction_type TEXT DEFAULT 'buy';
            """
            await conn.execute(add_column_query)
            print("✅ Колонка transaction_type добавлена как TEXT")
        except Exception as e:
            if "already exists" in str(e):
                print("✅ Колонка уже существует как TEXT")
            else:
                raise
        
        # Обновляем все существующие записи на uppercase
        update_existing_query = """
        UPDATE coin_transactions 
        SET transaction_type = 'BUY' 
        WHERE transaction_type IS NULL OR transaction_type = '' OR transaction_type = 'buy';
        """
        result = await conn.execute(update_existing_query)
        print(f"✅ Обновлено существующих записей: {result}")
        
        # Теперь создаем ENUM тип с правильными значениями
        create_enum_query = """
        DO $$ BEGIN
            CREATE TYPE transactiontype AS ENUM ('BUY', 'SELL');
        EXCEPTION
            WHEN duplicate_object THEN 
                -- Если тип уже существует, пересоздаем его
                DROP TYPE IF EXISTS transactiontype CASCADE;
                CREATE TYPE transactiontype AS ENUM ('BUY', 'SELL');
        END $$;
        """
        await conn.execute(create_enum_query)
        print("✅ ENUM тип создан с правильными значениями")
        
        # Убираем DEFAULT перед изменением типа
        remove_default_query = """
        ALTER TABLE coin_transactions 
        ALTER COLUMN transaction_type DROP DEFAULT;
        """
        await conn.execute(remove_default_query)
        print("✅ DEFAULT убран")
        
        # Изменяем тип колонки на ENUM
        alter_column_query = """
        ALTER TABLE coin_transactions 
        ALTER COLUMN transaction_type TYPE transactiontype 
        USING transaction_type::transactiontype;
        """
        await conn.execute(alter_column_query)
        print("✅ Колонка преобразована в ENUM тип")
        
        # Устанавливаем новый DEFAULT для ENUM
        set_default_query = """
        ALTER TABLE coin_transactions 
        ALTER COLUMN transaction_type SET DEFAULT 'BUY'::transactiontype;
        """
        await conn.execute(set_default_query)
        print("✅ DEFAULT установлен для ENUM")
        
        await conn.close()
        
        return {
            "status": "success", 
            "message": "Миграция успешно завершена",
            "details": "Колонка transaction_type добавлена и настроена"
        }
        
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        return {
            "status": "error",
            "message": f"Ошибка при миграции: {str(e)}"
        }

@api_router.post("/admin/simple-migration")
async def simple_migration():
    """Простая миграция - добавить transaction_type как TEXT"""
    try:
        import asyncpg
        from shared.config import settings
        
        # Получаем URL базы данных
        if settings.DATABASE_URL:
            db_url = settings.DATABASE_URL
        else:
            db_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        
        print("Простая миграция...")
        
        # Подключаемся к базе данных
        conn = await asyncpg.connect(db_url)
        
        # Проверяем, существует ли колонка
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'coin_transactions' 
        AND column_name = 'transaction_type';
        """
        
        existing = await conn.fetchval(check_query)
        
        if not existing:
            # Добавляем колонку как TEXT
            add_query = """
            ALTER TABLE coin_transactions 
            ADD COLUMN transaction_type TEXT DEFAULT 'BUY';
            """
            await conn.execute(add_query)
            print("✅ Колонка transaction_type добавлена как TEXT")
        
        # Обновляем все NULL значения на 'BUY'
        update_query = """
        UPDATE coin_transactions 
        SET transaction_type = 'BUY' 
        WHERE transaction_type IS NULL OR transaction_type = '';
        """
        result = await conn.execute(update_query)
        print(f"✅ Обновлено записей: {result}")
        
        await conn.close()
        
        return {
            "status": "success", 
            "message": "Простая миграция завершена",
            "column_exists": existing is not None,
            "updated_records": result if not existing else "N/A"
        }
        
    except Exception as e:
        print(f"❌ Ошибка при простой миграции: {e}")
        return {
            "status": "error",
            "message": f"Ошибка: {str(e)}"
        }

@api_router.post("/admin/fix-transaction-enum")
async def fix_transaction_enum():
    """Исправить значения ENUM в существующих записях"""
    try:
        import asyncpg
        from shared.config import settings
        
        # Получаем URL базы данных
        if settings.DATABASE_URL:
            db_url = settings.DATABASE_URL
        else:
            db_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        
        print("Исправляем значения ENUM...")
        
        # Подключаемся к базе данных
        conn = await asyncpg.connect(db_url)
        
        # Пересоздаем ENUM тип с правильными значениями
        recreate_enum_query = """
        -- Удаляем старый тип и создаем новый
        DROP TYPE IF EXISTS transactiontype CASCADE;
        CREATE TYPE transactiontype AS ENUM ('BUY', 'SELL');
        """
        await conn.execute(recreate_enum_query)
        print("✅ ENUM тип пересоздан")
        
        # Изменяем колонку обратно на TEXT временно
        to_text_query = """
        ALTER TABLE coin_transactions 
        ALTER COLUMN transaction_type TYPE TEXT;
        """
        await conn.execute(to_text_query)
        print("✅ Колонка изменена на TEXT")
        
        # Обновляем значения на uppercase
        update_values_query = """
        UPDATE coin_transactions 
        SET transaction_type = UPPER(transaction_type);
        """
        result = await conn.execute(update_values_query)
        print(f"✅ Обновлено значений: {result}")
        
        # Изменяем обратно на ENUM
        to_enum_query = """
        ALTER TABLE coin_transactions 
        ALTER COLUMN transaction_type TYPE transactiontype 
        USING transaction_type::transactiontype;
        """
        await conn.execute(to_enum_query)
        print("✅ Колонка изменена на ENUM")
        
        await conn.close()
        
        return {
            "status": "success", 
            "message": "ENUM значения исправлены",
            "details": f"Обновлено записей: {result}"
        }
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении ENUM: {e}")
        return {
            "status": "error",
            "message": f"Ошибка при исправлении ENUM: {str(e)}"
        }

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

async def get_coin_cache_repository(session: AsyncSession = Depends(get_async_session)):
    return SQLAlchemyCoinCacheRepository(session)

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
                id=None,  # Явно указываем None для нового пользователя
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
            transaction_type=APITransactionType.BUY,
            total_amount=request.quantity * request.price
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка в add_coin_to_portfolio: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении монеты: {str(e)}")

@api_router.post("/portfolio/sell-coin", response_model=TransactionResponse)
async def sell_coin_from_portfolio(
    request: SellCoinRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    portfolio_repo: SQLAlchemyPortfolioRepository = Depends(get_portfolio_repository),
    transaction_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository)
):
    """Продать монету из портфеля"""
    
    try:
        # Логируем запрос для отладки
        print(f"Получен запрос на продажу монеты: {request}")
        
        use_case = SellCoinFromPortfolioUseCase(user_repo, portfolio_repo, transaction_repo)
        
        success = await use_case.execute(
            telegram_id=request.telegram_id,
            symbol=request.symbol,
            quantity=request.quantity,
            price=request.price
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Ошибка при продаже монеты: недостаточно монет или монета не найдена")
        
        return TransactionResponse(
            symbol=request.symbol,
            name="",  # Имя будет получено из портфеля
            quantity=request.quantity,
            price=request.price,
            transaction_type=APITransactionType.SELL,
            total_amount=request.quantity * request.price
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка в sell_coin_from_portfolio: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при продаже монеты: {str(e)}")

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
                transaction_type=APITransactionType.BUY if tx.transaction_type == TransactionType.BUY else APITransactionType.SELL,
                timestamp=tx.timestamp
            )
            for tx in transactions
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении транзакций: {str(e)}")

@api_router.get("/market/top-coins", response_model=List[CoinDataResponse])
async def get_top_coins(
    limit: int = 100, 
    response: Response = None,
    cache_repo: SQLAlchemyCoinCacheRepository = Depends(get_coin_cache_repository)
):
    """Получить топ монет по рыночной капитализации (с кэшированием)"""
    
    # Добавляем CORS заголовки
    if response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    try:
        # Проверяем, актуален ли кэш (обновляем каждые 5 минут)
        is_fresh = await cache_repo.is_cache_fresh('top_coins', max_age_minutes=5)
        
        print(f"🔍 Проверка кэша топ монет: свежий={is_fresh}")
        
        if is_fresh:
            print("📦 Используем кэшированные данные топ монет")
            cached_coins = await cache_repo.get_cached_coins('top_coins', limit)
            print(f"📊 Получено из кэша: {len(cached_coins)} монет")
            
            if cached_coins:
                result = [
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
                    for coin in cached_coins
                ]
                print(f"✅ Возвращаем {len(result)} монет из кэша")
                return result
        
        # Если кэш устарел, обновляем данные из API
        print("🔄 Обновляем кэш топ монет из API")
        import asyncio
        async with CoinGeckoAPI() as api:
            coins = await asyncio.wait_for(
                api.get_top_coins(limit),
                timeout=15.0  # 15 секунд timeout
            )
            
            if coins:
                # Сохраняем в кэш
                await cache_repo.update_cache(coins, 'top_coins')
                print("✅ Кэш топ монет обновлен")
                
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
    
    except asyncio.TimeoutError:
        print("⏱️ Timeout при получении топ монет из API, пытаемся вернуть устаревший кэш")
        # Если API не отвечает, возвращаем устаревший кэш
        cached_coins = await cache_repo.get_cached_coins('top_coins', limit)
        if cached_coins:
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
                for coin in cached_coins
            ]
    except Exception as e:
        print(f"❌ Ошибка при получении топ монет: {e}")
        # В случае ошибки пытаемся вернуть кэш
        try:
            cached_coins = await cache_repo.get_cached_coins('top_coins', limit)
            if cached_coins:
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
                    for coin in cached_coins
                ]
        except:
            pass
    
    # Последний fallback: возвращаем минимальные тестовые данные
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
async def get_growth_leaders(
    limit: int = 5, 
    response: Response = None,
    cache_repo: SQLAlchemyCoinCacheRepository = Depends(get_coin_cache_repository)
):
    """Получить лидеров роста за 24 часа (с кэшированием)"""
    
    # Добавляем CORS заголовки
    if response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    try:
        # Проверяем, актуален ли кэш (обновляем каждые 10 минут)
        is_fresh = await cache_repo.is_cache_fresh('growth_leaders', max_age_minutes=10)
        
        if is_fresh:
            print("📦 Используем кэшированные данные лидеров роста")
            cached_coins = await cache_repo.get_cached_coins('growth_leaders', limit)
            if cached_coins:
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
                    for coin in cached_coins
                ]
        
        # Если кэш устарел, обновляем данные из API
        print("🔄 Обновляем кэш лидеров роста из API")
        import asyncio
        async with CoinGeckoAPI() as api:
            coins = await asyncio.wait_for(
                api.get_growth_leaders(limit),
                timeout=15.0
            )
            
            if coins:
                # Сохраняем в кэш
                await cache_repo.update_cache(coins, 'growth_leaders')
                print("✅ Кэш лидеров роста обновлен")
                
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
    
    except asyncio.TimeoutError:
        print("⏱️ Timeout при получении лидеров роста из API")
        cached_coins = await cache_repo.get_cached_coins('growth_leaders', limit)
        if cached_coins:
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
                for coin in cached_coins
            ]
    except Exception as e:
        print(f"❌ Ошибка при получении лидеров роста: {e}")
        try:
            cached_coins = await cache_repo.get_cached_coins('growth_leaders', limit)
            if cached_coins:
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
                    for coin in cached_coins
                ]
        except:
            pass
    
    # Fallback: возвращаем статичные данные
    return [
        CoinDataResponse(
            id="solana",
            symbol="SOL",
            name="Solana",
            current_price=203.71,
            market_cap=110270000000.0,
            market_cap_rank=6,
            price_change_percentage_24h=8.5,
            image="https://coin-images.coingecko.com/coins/images/4128/large/solana.png",
            total_volume=2924728071.0
        ),
        CoinDataResponse(
            id="chainlink",
            symbol="LINK",
            name="Chainlink",
            current_price=22.27,
            market_cap=15090000000.0,
            market_cap_rank=11,
            price_change_percentage_24h=6.8,
            image="https://coin-images.coingecko.com/coins/images/877/large/chainlink.png",
            total_volume=800000000.0
        ),
        CoinDataResponse(
            id="avalanche-2",
            symbol="AVAX",
            name="Avalanche",
            current_price=45.20,
            market_cap=18500000000.0,
            market_cap_rank=9,
            price_change_percentage_24h=5.2,
            image="https://coin-images.coingecko.com/coins/images/12559/large/Avalanche_Circle_RedWhite_Trans.png",
            total_volume=650000000.0
        ),
        CoinDataResponse(
            id="polygon",
            symbol="MATIC",
            name="Polygon",
            current_price=0.52,
            market_cap=5200000000.0,
            market_cap_rank=18,
            price_change_percentage_24h=4.8,
            image="https://coin-images.coingecko.com/coins/images/4713/large/polygon.png",
            total_volume=300000000.0
        ),
        CoinDataResponse(
            id="uniswap",
            symbol="UNI",
            name="Uniswap",
            current_price=15.80,
            market_cap=9500000000.0,
            market_cap_rank=15,
            price_change_percentage_24h=3.9,
            image="https://coin-images.coingecko.com/coins/images/12504/large/uniswap.jpg",
            total_volume=180000000.0
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

@api_router.post("/admin/refresh-coin-cache")
async def refresh_coin_cache(
    cache_repo: SQLAlchemyCoinCacheRepository = Depends(get_coin_cache_repository)
):
    """Принудительно обновить кэш монет из API (админ endpoint)"""
    try:
        import asyncio
        
        results = {
            "top_coins": False,
            "growth_leaders": False,
            "errors": []
        }
        
        # Обновляем топ монеты
        try:
            print("🔄 Обновляем кэш топ монет...")
            async with CoinGeckoAPI() as api:
                coins = await asyncio.wait_for(api.get_top_coins(100), timeout=20.0)
                if coins:
                    await cache_repo.update_cache(coins, 'top_coins')
                    results["top_coins"] = True
                    print("✅ Кэш топ монет обновлен")
        except Exception as e:
            error_msg = f"Ошибка при обновлении топ монет: {str(e)}"
            print(f"❌ {error_msg}")
            results["errors"].append(error_msg)
        
        # Обновляем лидеров роста
        try:
            print("🔄 Обновляем кэш лидеров роста...")
            async with CoinGeckoAPI() as api:
                coins = await asyncio.wait_for(api.get_growth_leaders(20), timeout=20.0)
                if coins:
                    await cache_repo.update_cache(coins, 'growth_leaders')
                    results["growth_leaders"] = True
                    print("✅ Кэш лидеров роста обновлен")
        except Exception as e:
            error_msg = f"Ошибка при обновлении лидеров роста: {str(e)}"
            print(f"❌ {error_msg}")
            results["errors"].append(error_msg)
        
        return {
            "status": "completed",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Критическая ошибка при обновлении кэша: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении кэша: {str(e)}")


 