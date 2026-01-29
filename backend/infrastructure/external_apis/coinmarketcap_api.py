"""
CoinMarketCap API для получения данных о криптовалютах
Бесплатный tier: 10,000 запросов/месяц
"""
import aiohttp
from decimal import Decimal
from typing import Optional, Dict, Any, List
import asyncio


class CoinMarketCapAPI:
    """API для работы с CoinMarketCap"""
    
    def __init__(self, api_key: str):
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_top_coins(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить топ монет по рыночной капитализации"""
        try:
            url = f"{self.base_url}/cryptocurrency/listings/latest"
            params = {
                'start': 1,
                'limit': limit,
                'convert': 'USD',
                'sort': 'market_cap',
                'sort_dir': 'desc'
            }
            
            print(f"🌐 Запрос к CoinMarketCap API: {url}")
            print(f"📊 Параметры: limit={limit}")
            
            if not self.session:
                headers = {
                    'X-CMC_PRO_API_KEY': self.api_key,
                    'Accept': 'application/json'
                }
                async with aiohttp.ClientSession(headers=headers) as session:
                    return await self._fetch_coins_data(session, url, params)
            
            return await self._fetch_coins_data(self.session, url, params)
            
        except Exception as e:
            print(f"❌ Ошибка при получении топ монет: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def get_growth_leaders(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить лидеров роста за 24 часа"""
        try:
            # Получаем больше монет и фильтруем по росту
            url = f"{self.base_url}/cryptocurrency/listings/latest"
            params = {
                'start': 1,
                'limit': limit * 5,  # Берем больше для фильтрации
                'convert': 'USD',
                'sort': 'percent_change_24h',
                'sort_dir': 'desc'
            }
            
            print(f"🌐 Запрос лидеров роста к CoinMarketCap API: {url}")
            
            if not self.session:
                headers = {
                    'X-CMC_PRO_API_KEY': self.api_key,
                    'Accept': 'application/json'
                }
                async with aiohttp.ClientSession(headers=headers) as session:
                    return await self._fetch_growth_leaders_data(session, url, params, limit)
            
            return await self._fetch_growth_leaders_data(self.session, url, params, limit)
            
        except Exception as e:
            print(f"❌ Ошибка при получении лидеров роста: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _fetch_coins_data(self, session: aiohttp.ClientSession, url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить данные о монетах"""
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as response:
                print(f"📡 Получен ответ: HTTP {response.status}")
                
                if response.status == 429:
                    print("⚠️ Rate limit превышен")
                    return []
                elif response.status == 401:
                    print("❌ Неверный API ключ CoinMarketCap")
                    return []
                elif response.status != 200:
                    error_text = await response.text()
                    print(f"❌ HTTP {response.status}: {error_text}")
                    return []
                
                data = await response.json()
                
                if 'data' not in data:
                    print("⚠️ Нет данных в ответе")
                    return []
                
                coins_data = data['data']
                print(f"📦 Получено данных: {len(coins_data)} монет")
                
                result = []
                for coin in coins_data:
                    try:
                        quote = coin['quote']['USD']
                        coin_data = {
                            'id': coin['slug'],  # используем slug как id
                            'symbol': coin['symbol'],
                            'name': coin['name'],
                            'current_price': quote['price'],
                            'market_cap': quote['market_cap'],
                            'market_cap_rank': coin['cmc_rank'],
                            'price_change_percentage_24h': quote['percent_change_24h'],
                            'image': f"https://s2.coinmarketcap.com/static/img/coins/64x64/{coin['id']}.png",
                            'total_volume': quote['volume_24h']
                        }
                        result.append(coin_data)
                    except (KeyError, TypeError) as e:
                        print(f"⚠️ Ошибка обработки монеты {coin.get('symbol', 'unknown')}: {e}")
                        continue
                
                print(f"✅ Обработано успешно: {len(result)} монет")
                return result
                
        except asyncio.TimeoutError:
            print("⏱️ Timeout при получении данных о монетах")
            return []
        except Exception as e:
            print(f"❌ Ошибка при получении данных: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _fetch_growth_leaders_data(self, session: aiohttp.ClientSession, url: str, params: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Получить данные лидеров роста с фильтрацией"""
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as response:
                print(f"📡 Получен ответ: HTTP {response.status}")
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ HTTP {response.status}: {error_text}")
                    return []
                
                data = await response.json()
                
                if 'data' not in data:
                    print("⚠️ Нет данных в ответе")
                    return []
                
                coins_data = data['data']
                print(f"📦 Получено данных: {len(coins_data)} монет")
                
                # Фильтруем только монеты с положительным ростом
                growth_leaders = []
                for coin in coins_data:
                    try:
                        quote = coin['quote']['USD']
                        price_change = quote.get('percent_change_24h', 0)
                        
                        if price_change and price_change > 0:  # Только с положительным ростом
                            coin_data = {
                                'id': coin['slug'],
                                'symbol': coin['symbol'],
                                'name': coin['name'],
                                'current_price': quote['price'],
                                'market_cap': quote['market_cap'],
                                'market_cap_rank': coin['cmc_rank'],
                                'price_change_percentage_24h': quote['percent_change_24h'],
                                'image': f"https://s2.coinmarketcap.com/static/img/coins/64x64/{coin['id']}.png",
                                'total_volume': quote['volume_24h']
                            }
                            growth_leaders.append(coin_data)
                            
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
    
    async def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Получить текущие цены монет по символам"""
        try:
            url = f"{self.base_url}/cryptocurrency/quotes/latest"
            params = {
                'symbol': ','.join(symbols),
                'convert': 'USD'
            }
            
            print(f"🌐 Запрос цен к CoinMarketCap: {symbols}")
            
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ HTTP {response.status}: {error_text}")
                    return {}
                
                data = await response.json()
                
                if 'data' not in data:
                    return {}
                
                result = {}
                for symbol, coin_data in data['data'].items():
                    try:
                        price = coin_data['quote']['USD']['price']
                        result[symbol.lower()] = price
                        print(f"💰 {symbol}: ${price}")
                    except (KeyError, TypeError) as e:
                        print(f"⚠️ Ошибка получения цены для {symbol}: {e}")
                        continue
                
                print(f"✅ Получено цен: {len(result)}")
                return result
                
        except Exception as e:
            print(f"❌ Ошибка при получении цен: {e}")
            return {}
