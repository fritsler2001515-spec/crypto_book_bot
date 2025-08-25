import aiohttp
from decimal import Decimal
from typing import Optional, Dict, Any, List
import asyncio


class CoinGeckoAPI:
    """API для работы с CoinGecko"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        # Создаем сессию с отключенной проверкой SSL для разработки
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_top_coins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить топ монет по рыночной капитализации"""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': 'false',
                'locale': 'ru'
            }
            
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=False)
                async with aiohttp.ClientSession(connector=connector) as session:
                    return await self._fetch_coins_data(session, url, params)
            return await self._fetch_coins_data(self.session, url, params)
            
        except Exception as e:
            print(f"Ошибка при получении топ монет: {e}")
            return []
    
    async def get_growth_leaders(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Получить лидеров роста за 24 часа"""
        try:
            # Получаем монеты, отсортированные по проценту изменения цены за 24ч
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'percent_change_24h_desc',  # Сортировка по росту за 24ч
                'per_page': limit,
                'page': 1,
                'sparkline': 'false',
                'locale': 'ru'
            }
            
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=False)
                async with aiohttp.ClientSession(connector=connector) as session:
                    return await self._fetch_coins_data(session, url, params)
            return await self._fetch_coins_data(self.session, url, params)
            
        except Exception as e:
            print(f"Ошибка при получении лидеров роста: {e}")
            return []
    
    async def _fetch_coins_data(self, session: aiohttp.ClientSession, url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить данные о монетах"""
        try:
            # Добавляем задержку перед запросом для избежания rate limit
            await asyncio.sleep(1)
            
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    print("Rate limit превышен. Ожидание 10 секунд...")
                    await asyncio.sleep(10)
                    return []
                elif response.status != 200:
                    error_text = await response.text()
                    print(f"HTTP {response.status}: {error_text}")
                    return []
                
                data = await response.json()
                
                if not data:
                    return []
                
                result = []
                for coin in data:
                    try:
                        result.append({
                            'id': coin['id'],
                            'symbol': coin['symbol'].upper(),
                            'name': coin['name'],
                            'current_price': coin['current_price'],
                            'market_cap': coin['market_cap'],
                            'market_cap_rank': coin['market_cap_rank'],
                            'price_change_percentage_24h': coin['price_change_percentage_24h'],
                            'image': coin['image'],
                            'total_volume': coin['total_volume']
                        })
                    except KeyError as e:
                        print(f"Отсутствует поле {e} в данных монеты")
                        continue
                
                return result
                
        except Exception as e:
            print(f"Ошибка при получении данных о монетах: {e}")
            return []

    async def get_price_by_name(self, coin_name: str) -> Optional[Decimal]:
        """Получить цену монеты по названию"""
        if not self.session:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                return await self._fetch_price(session, coin_name)
        return await self._fetch_price(self.session, coin_name)
    
    async def get_prices_batch(self, coin_names: list[str]) -> Dict[str, Decimal]:
        """Получить цены для нескольких монет"""
        if not self.session:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                return await self._fetch_prices_batch(session, coin_names)
        return await self._fetch_prices_batch(self.session, coin_names)
    
    async def _fetch_price(self, session: aiohttp.ClientSession, coin_name: str) -> Optional[Decimal]:
        """Получить цену одной монеты"""
        try:
            # Поиск монеты
            search_url = f"{self.base_url}/search?query={coin_name.lower().strip()}"
            async with session.get(search_url) as response:
                if response.status != 200:
                    print(f"HTTP {response.status} при поиске монеты {coin_name}")
                    return None
                
                data = await response.json()
                results = data.get("coins", [])
                
                if not results:
                    print(f"Монета '{coin_name}' не найдена")
                    return None
                
                # Берем первую найденную монету
                coin_id = results[0]["id"]
                coin_name_found = results[0]["name"]
                
                # Проверяем, что найденная монета похожа на запрошенную
                if coin_name.lower() not in coin_name_found.lower() and coin_name_found.lower() not in coin_name.lower():
                    print(f"Предупреждение: запрошена '{coin_name}', найдена '{coin_name_found}'")
            
            # Получение цены
            price_url = f"{self.base_url}/simple/price?ids={coin_id}&vs_currencies=usd"
            async with session.get(price_url) as response:
                if response.status != 200:
                    print(f"HTTP {response.status} при получении цены для {coin_name}")
                    return None
                
                data = await response.json()
                if coin_id not in data:
                    print(f"Цена для {coin_name} (ID: {coin_id}) не найдена в ответе")
                    return None
                
                price = data[coin_id]["usd"]
                if price is None:
                    print(f"Цена для {coin_name} равна None")
                    return None
                
                return Decimal(str(price))
                
        except Exception as e:
            print(f"Ошибка при получении цены для {coin_name}: {e}")
            return None
    
    async def _fetch_prices_batch(self, session: aiohttp.ClientSession, coin_names: list[str]) -> Dict[str, Decimal]:
        """Получить цены для нескольких монет"""
        results = {}
        
        # Получаем все цены параллельно
        tasks = []
        for coin_name in coin_names:
            task = self._fetch_price(session, coin_name)
            tasks.append((coin_name, task))
        
        # Выполняем все запросы параллельно
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Обрабатываем результаты
        for i, (coin_name, _) in enumerate(tasks):
            result = completed_tasks[i]
            if isinstance(result, Exception):
                print(f"Ошибка при получении цены для {coin_name}: {result}")
            elif result is not None:
                results[coin_name] = result
        
        return results


# Синхронная версия для обратной совместимости
def fetch_price_by_name(user_input: str) -> Decimal:
    """Синхронная версия для обратной совместимости"""
    async def _async_fetch():
        async with CoinGeckoAPI() as api:
            return await api.get_price_by_name(user_input)
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если мы уже в асинхронном контексте, создаем новую задачу
            # и ждем её завершения
            future = asyncio.create_task(_async_fetch())
            # Возвращаем None, так как в асинхронном контексте нужно использовать await
            return None
        else:
            # Если мы в синхронном контексте
            return asyncio.run(_async_fetch())
    except Exception as e:
        print(f"Ошибка в fetch_price_by_name: {e}")
        return Decimal("0")
