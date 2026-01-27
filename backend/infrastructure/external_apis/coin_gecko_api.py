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
                'order': 'price_change_percentage_24h_desc',  # Правильная сортировка по росту за 24ч
                'per_page': limit * 3,  # Берем больше монет для фильтрации
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h'  # Включаем данные о изменении цены
            }
            
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=False)
                async with aiohttp.ClientSession(connector=connector) as session:
                    return await self._fetch_growth_leaders_data(session, url, params, limit)
            return await self._fetch_growth_leaders_data(self.session, url, params, limit)
            
        except Exception as e:
            print(f"Ошибка при получении лидеров роста: {e}")
            return []
    
    async def _fetch_coins_data(self, session: aiohttp.ClientSession, url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить данные о монетах"""
        try:
            # Задержка перед запросом для избежания rate limit
            await asyncio.sleep(2)
            
            print(f"🌐 Запрос к CoinGecko API: {url}")
            print(f"📊 Параметры: {params}")
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as response:
                print(f"📡 Получен ответ: HTTP {response.status}")
                
                if response.status == 429:
                    print("⚠️ Rate limit превышен. Используем fallback данные")
                    return []
                elif response.status != 200:
                    error_text = await response.text()
                    print(f"❌ HTTP {response.status}: {error_text}")
                    return []
                
                data = await response.json()
                print(f"📦 Получено данных: {len(data) if data else 0} монет")
                
                if not data:
                    print("⚠️ Пустой ответ от API")
                    return []
                
                result = []
                for coin in data:
                    try:
                        coin_data = {
                            'id': coin['id'],
                            'symbol': coin['symbol'].upper(),
                            'name': coin['name'],
                            'current_price': coin['current_price'],
                            'market_cap': coin['market_cap'],
                            'market_cap_rank': coin['market_cap_rank'],
                            'price_change_percentage_24h': coin['price_change_percentage_24h'],
                            'image': coin['image'],
                            'total_volume': coin['total_volume']
                        }
                        result.append(coin_data)
                    except KeyError as e:
                        print(f"⚠️ Отсутствует поле {e} в данных монеты {coin.get('id', 'unknown')}")
                        continue
                
                print(f"✅ Обработано успешно: {len(result)} монет")
                return result
                
        except asyncio.TimeoutError:
            print("⏱️ Timeout при получении данных о монетах")
            return []
        except Exception as e:
            print(f"❌ Ошибка при получении данных о монетах: {e}")
            import traceback
            traceback.print_exc()
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
    
    async def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Получить текущие цены монет по символам (BTC, ETH, etc.)"""
        try:
            # Маппинг символов в ID CoinGecko
            symbol_to_id = {
                'btc': 'bitcoin',
                'eth': 'ethereum', 
                'usdt': 'tether',
                'bnb': 'binancecoin',
                'sol': 'solana',
                'xrp': 'ripple',
                'usdc': 'usd-coin',
                'ada': 'cardano',
                'doge': 'dogecoin',
                'trx': 'tron',
                'avax': 'avalanche-2',
                'dot': 'polkadot',
                'matic': 'matic-network',
                'ltc': 'litecoin',
                'link': 'chainlink',
                'ape': 'apecoin',  # Добавляем APE
                'atom': 'cosmos',
                'near': 'near',
                'uni': 'uniswap',
                'shib': 'shiba-inu',
                'pepe': 'pepe',
                'wif': 'dogwifcoin',
                'bonk': 'bonk',
                'floki': 'floki',
            }
            
            # Преобразуем символы в ID
            coin_ids = []
            missing_symbols = []
            for symbol in symbols:
                symbol_lower = symbol.lower()
                if symbol_lower in symbol_to_id:
                    coin_ids.append(symbol_to_id[symbol_lower])
                else:
                    missing_symbols.append(symbol)
            
            # Для отсутствующих символов пытаемся найти через поиск
            if missing_symbols:
                print(f"🔍 Ищем отсутствующие символы: {missing_symbols}")
                for symbol in missing_symbols:
                    try:
                        # Ищем монету через search API
                        search_url = f"{self.base_url}/search?query={symbol}"
                        
                        if not self.session:
                            connector = aiohttp.TCPConnector(ssl=False)
                            async with aiohttp.ClientSession(connector=connector) as session:
                                async with session.get(search_url) as search_response:
                                    if search_response.status == 200:
                                        search_data = await search_response.json()
                                        coins = search_data.get('coins', [])
                                        # Берем первую найденную монету с точным совпадением символа
                                        for coin in coins:
                                            if coin.get('symbol', '').upper() == symbol.upper():
                                                coin_id = coin.get('id')
                                                if coin_id:
                                                    print(f"✅ Найден {symbol}: {coin_id}")
                                                    coin_ids.append(coin_id)
                                                    symbol_to_id[symbol.lower()] = coin_id
                                                break
                        else:
                            async with self.session.get(search_url) as search_response:
                                if search_response.status == 200:
                                    search_data = await search_response.json()
                                    coins = search_data.get('coins', [])
                                    # Берем первую найденную монету с точным совпадением символа
                                    for coin in coins:
                                        if coin.get('symbol', '').upper() == symbol.upper():
                                            coin_id = coin.get('id')
                                            if coin_id:
                                                print(f"✅ Найден {symbol}: {coin_id}")
                                                coin_ids.append(coin_id)
                                                symbol_to_id[symbol.lower()] = coin_id
                                            break
                        
                        await asyncio.sleep(0.1)  # Задержка между поисками
                    except Exception as search_error:
                        print(f"❌ Ошибка поиска {symbol}: {search_error}")
            
            if not coin_ids:
                print("❌ Нет монет для обновления цен после поиска")
                return {}
            
            # Делаем запрос к API
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd'
            }
            
            # Добавляем задержку для избежания rate limit
            await asyncio.sleep(0.1)
            
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=False)
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 429:  # Rate limit
                            print("Rate limit превышен. Ожидание 10 секунд...")
                            await asyncio.sleep(10)
                            return {}
                        
                        if response.status == 200:
                            data = await response.json()
                            print(f"📊 Получены данные от CoinGecko: {data}")
                            
                            # Преобразуем обратно в символы
                            result = {}
                            id_to_symbol = {v: k for k, v in symbol_to_id.items()}
                            
                            for coin_id, price_data in data.items():
                                if coin_id in id_to_symbol:
                                    symbol = id_to_symbol[coin_id]
                                    price = price_data.get('usd', 0)
                                    result[symbol] = price
                                    print(f"💰 {symbol.upper()}: ${price}")
                            
                            print(f"✅ Итого получено цен: {len(result)}")
                            return result
            
            return {}
            
        except Exception as e:
            print(f"Ошибка при получении цен: {e}")
            return {}
    
    async def _fetch_growth_leaders_data(self, session: aiohttp.ClientSession, url: str, params: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Получить данные лидеров роста с фильтрацией"""
        try:
            # Задержка перед запросом для избежания rate limit
            await asyncio.sleep(2)
            
            print(f"🌐 Запрос лидеров роста к CoinGecko API: {url}")
            print(f"📊 Параметры: {params}")
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as response:
                print(f"📡 Получен ответ: HTTP {response.status}")
                
                if response.status == 429:
                    print("⚠️ Rate limit превышен. Используем fallback данные")
                    return []
                elif response.status != 200:
                    error_text = await response.text()
                    print(f"❌ HTTP {response.status}: {error_text}")
                    return []
                
                data = await response.json()
                print(f"📦 Получено данных: {len(data) if data else 0} монет")
                
                if not data:
                    print("⚠️ Пустой ответ от API")
                    return []
                
                # Фильтруем только монеты с положительным ростом
                growth_leaders = []
                for coin in data:
                    try:
                        price_change = coin.get('price_change_percentage_24h', 0)
                        if price_change and price_change > 0:  # Только с положительным ростом
                            growth_leaders.append({
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
                            
                            if len(growth_leaders) >= limit:
                                break
                    except (KeyError, TypeError) as e:
                        print(f"⚠️ Ошибка обработки монеты: {e}")
                        continue
                
                print(f"✅ Найдено лидеров роста: {len(growth_leaders)}")
                return growth_leaders
                
        except asyncio.TimeoutError:
            print("⏱️ Timeout при получении лидеров роста")
            return []
        except Exception as e:
            print(f"❌ Ошибка при получении лидеров роста: {e}")
            import traceback
            traceback.print_exc()
            return []


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
