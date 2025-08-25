# Настройка API между фронтендом и бэкендом

## Обзор архитектуры

Проект использует следующую архитектуру:
- **Бэкенд**: FastAPI на Python (порт 8001)
- **Фронтенд**: React TypeScript с прокси настройкой
- **База данных**: PostgreSQL

## Исправленные проблемы

### 1. ✅ Типы данных
**Проблема**: Несоответствие типов между бэкендом (Decimal) и фронтендом (number | string)
**Решение**: 
- Обновлены схемы Pydantic для правильной сериализации Decimal в float
- Исправлены типы TypeScript для соответствия бэкенду

### 2. ✅ Пути API
**Проблема**: Неправильные пути API в запросах фронтенда
**Решение**: 
- Добавлен префикс `/api` ко всем запросам фронтенда
- Соответствует монтированию в `main.py`: `app.mount("/api", fastapi_app)`

### 3. ✅ Обработка ошибок
**Проблема**: Отсутствие единообразной обработки ошибок
**Решение**:
- Добавлена схема `ErrorResponse` для типизированных ошибок
- Улучшена обработка исключений во всех endpoints

## Конфигурация

### Бэкенд (FastAPI)
```python
# main.py
app.mount("/api", fastapi_app)  # API доступен по пути /api

# Порт: 8001 (настраивается в config.py)
API_PORT: int = int(os.getenv("API_PORT", "8001"))
```

### Фронтенд (React)
```json
// package.json
"proxy": "http://localhost:8001"
```

```typescript
// api.ts
const BACKEND_URL = process.env.REACT_APP_API_URL || '';
// Все запросы идут на /api/endpoint
```

## Endpoints API

### Пользователи
- `GET /api/users/{telegram_id}` - Получить пользователя
- `GET /api/portfolio/{telegram_id}` - Получить портфель
- `POST /api/portfolio/add-coin` - Добавить монету
- `GET /api/transactions/{telegram_id}` - Получить транзакции

### Рынок
- `GET /api/market/top-coins` - Топ монет
- `GET /api/market/growth-leaders` - Лидеры роста
- `GET /api/prices/{coin_names}` - Текущие цены

### Система
- `GET /api/status` - Статус API
- `GET /health` - Проверка здоровья

## Типы данных

### Бэкенд (Pydantic)
```python
class PortfolioItemResponse(BaseModel):
    id: int
    user_id: int
    symbol: str
    name: str
    total_quantity: Decimal  # Автоматически конвертируется в float
    avg_price: Decimal
    current_price: Decimal
    total_spent: Decimal
    last_updated: datetime
```

### Фронтенд (TypeScript)
```typescript
interface PortfolioItem {
  id: number;
  user_id: number;
  symbol: string;
  name: string;
  total_quantity: number;  // Соответствует Decimal с бэкенда
  avg_price: number;
  current_price: number;
  total_spent: number;
  last_updated: string;
}
```

## Запуск

### Локальная разработка
```bash
# Бэкенд
cd backend
python main.py

# Фронтенд (в другом терминале)
cd frontend
npm start
```

### Проверка работоспособности
1. Бэкенд: http://localhost:8001/api/status
2. Фронтенд: http://localhost:3000 (проксирует запросы на бэкенд)

## Безопасность

### CORS
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Для продакшена**: Ограничить `allow_origins` конкретными доменами.

## Отладка

### Проверка API
```bash
# Проверка статуса
curl http://localhost:8001/api/status

# Проверка портфеля (замените telegram_id)
curl http://localhost:8001/api/portfolio/123456789
```

### Логи
- Бэкенд: Логи в консоли при запуске
- Фронтенд: Логи в браузере (F12 → Console)

## Известные ограничения

1. **Decimal сериализация**: Все Decimal значения конвертируются в float для JSON
2. **Прокси**: Работает только в development режиме
3. **CORS**: Настроен для всех доменов (только для разработки)

## Рекомендации для продакшена

1. Настроить CORS для конкретных доменов
2. Добавить аутентификацию API
3. Настроить HTTPS
4. Добавить rate limiting
5. Настроить мониторинг и логирование
