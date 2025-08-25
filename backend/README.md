# Crypto Bot Backend

Бэкенд для криптобота с чистой архитектурой.

## Архитектура

```
backend/
├── domain/                    # Бизнес-логика (чистая)
│   ├── entities/             # Доменные сущности
│   ├── use_cases/            # Сценарии использования
│   └── repositories/         # Интерфейсы репозиториев
├── infrastructure/            # Внешние зависимости
│   ├── database/             # SQLAlchemy модели и репозитории
│   ├── telegram_bot/         # Telegram Bot API
│   └── external_apis/        # Внешние API (CoinGecko)
├── presentation/              # UI слой
│   ├── telegram_handlers/    # Telegram handlers
│   └── web_api/             # FastAPI endpoints
└── shared/                   # Общие компоненты
    ├── types/                # Pydantic схемы
    ├── config.py             # Конфигурация
    ├── states.py             # FSM состояния
    └── keyboards.py          # Клавиатуры
```

## База данных

Проект использует PostgreSQL для хранения данных.

### Структура таблиц

#### Таблица `users`
- `id` (Integer, Primary Key) - уникальный идентификатор пользователя
- `telegram_id` (BigInteger, Unique) - ID пользователя в Telegram
- `balance` (Numeric) - баланс пользователя

#### Таблица `user_portfolio`
- `id` (Integer, Primary Key) - уникальный идентификатор записи портфеля
- `user_id` (Integer, Foreign Key) - ссылка на пользователя
- `symbol` (Text) - символ криптовалюты (например, BTC)
- `name` (Text) - название криптовалюты (например, Bitcoin)
- `total_quantity` (Numeric) - количество монет
- `avg_price` (Numeric) - средняя цена покупки
- `current_price` (Numeric) - текущая цена
- `total_spent` (Numeric) - общая сумма потраченная на покупку
- `last_updated` (TIMESTAMP) - время последнего обновления

#### Таблица `coin_transactions`
- `id` (Integer, Primary Key) - уникальный идентификатор транзакции
- `user_id` (Integer, Foreign Key) - ссылка на пользователя
- `symbol` (Text) - символ криптовалюты
- `name` (Text) - название криптовалюты
- `quantity` (Numeric) - количество монет в транзакции
- `price` (Numeric) - цена за монету
- `total_spent` (Numeric) - общая сумма транзакции
- `timestamp` (TIMESTAMP) - время транзакции

## Установка

1. Создайте виртуальное окружение:
```bash
python -m .venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env`:
```env
BOT_TOKEN=your_telegram_bot_token
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASS=user123
```

4. Проверьте работу базы данных:
```bash
python scripts/init_db.py
```

## Запуск

### Разработка
```bash
python main.py
```

### Продакшн
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Портфель
- `GET /api/portfolio/{telegram_id}` - Получить портфель пользователя
- `POST /api/portfolio/add-coin` - Добавить монету в портфель

### Транзакции
- `GET /api/transactions/{telegram_id}` - Получить транзакции пользователя

### Пользователи
- `GET /api/user/{telegram_id}` - Получить информацию о пользователе

## Telegram Bot

Бот поддерживает следующие команды:
- `/start` - Начать работу с ботом
- `💼 Личный кабинет` - Показать личный кабинет
- `📊 Посмотреть портфель` - Показать портфель
- `➕ Добавить монету` - Добавить новую монету

## Тестирование

```bash
pytest tests/
```

## Структура проекта

### Domain Layer
- **Entities**: Доменные сущности (User, Portfolio, Transaction)
- **Use Cases**: Бизнес-логика (добавление монет, получение портфеля)
- **Repositories**: Интерфейсы для работы с данными

### Infrastructure Layer
- **Database**: SQLAlchemy модели и реализации репозиториев
- **External APIs**: Интеграция с CoinGecko API

### Presentation Layer
- **Telegram Handlers**: Обработчики Telegram сообщений
- **Web API**: FastAPI endpoints для фронтенда

### Shared
- **Types**: Pydantic схемы для API
- **Config**: Конфигурация приложения
- **States**: FSM состояния для Telegram бота
- **Keyboards**: Клавиатуры 