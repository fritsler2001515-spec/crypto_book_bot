# 🚀 CryptoBook Bot

Полнофункциональный криптобот с веб-интерфейсом для управления портфелем криптовалют.

## 📋 Описание

CryptoBook Bot - это комплексное решение для отслеживания криптопортфеля, состоящее из:

- **Telegram Bot** - для быстрого доступа через мессенджер
- **Web API** - REST API для интеграции
- **React Frontend** - современный веб-интерфейс
- **PostgreSQL Database** - надежное хранение данных

## 🏗️ Архитектура

```
crypto_book_bot/
├── backend/           # Python FastAPI бекенд
│   ├── domain/       # Бизнес-логика
│   ├── infrastructure/ # Внешние зависимости
│   ├── presentation/  # API и Telegram handlers
│   └── shared/       # Общие компоненты
├── frontend/         # React TypeScript фронтенд
│   ├── src/
│   │   ├── components/ # React компоненты
│   │   ├── pages/     # Страницы приложения
│   │   ├── services/  # API сервисы
│   │   └── types/     # TypeScript типы
│   └── public/       # Статические файлы
└── .env              # Конфигурация
```

## 🚀 Быстрый старт

### 1. Клонирование и установка

```bash
git clone <repository-url>
cd crypto_book_bot

# Активация виртуального окружения
source .venv/bin/activate

# Установка зависимостей бекенда
pip install -r backend/requirements.txt

# Установка зависимостей фронтенда
cd frontend
npm install
cd ..
```

### 2. Настройка базы данных

```bash
# Убедитесь, что PostgreSQL запущен
# Создайте базу данных и пользователя
# Обновите .env файл с вашими настройками БД
```

### 3. Запуск приложения

```bash
# Терминал 1: Запуск бекенда
cd backend
python main.py

# Терминал 2: Запуск фронтенда
cd frontend
npm start
```

### 4. Доступ к приложению

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs
- **Telegram Bot**: Найдите бота в Telegram

## 🎯 Возможности

### 📱 Telegram Bot
- Просмотр портфеля
- Добавление монет
- История транзакций
- Быстрые команды

### 🌐 Web Interface
- Современный темный дизайн
- Адаптивный интерфейс
- Детальная аналитика
- Удобные формы

### 🔌 API
- RESTful API
- Swagger документация
- Асинхронная обработка
- Валидация данных

## 🛠️ Технологии

### Backend
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **aiogram** - Telegram Bot API
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - типизация
- **Material-UI** - компоненты
- **React Router** - навигация
- **Axios** - HTTP клиент

## 📊 API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/status` | Статус сервера |
| GET | `/api/users/{telegram_id}` | Информация о пользователе |
| GET | `/api/portfolio/{telegram_id}` | Портфель пользователя |
| POST | `/api/portfolio/add-coin` | Добавить монету |
| GET | `/api/transactions/{telegram_id}` | Транзакции пользователя |

## 🔧 Конфигурация

Создайте файл `.env` в корне проекта:

```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token

# Database
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASS=your_password

# API
API_HOST=0.0.0.0
API_PORT=8001

# Chat IDs
CHAT_IDS=your_chat_id
```

## 🧪 Тестирование

```bash
# Тесты бекенда
cd backend
python -m pytest tests/ -v

# Тесты фронтенда
cd frontend
npm test
```

## 📦 Развертывание

### Development
```bash
# Бекенд
cd backend
python main.py

# Фронтенд
cd frontend
npm start
```

### Production
```bash
# Бекенд
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001

# Фронтенд
cd frontend
npm run build
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License

## 🆘 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте документацию
2. Создайте Issue в GitHub
3. Обратитесь к разработчикам

---

**CryptoBook Bot** - современное решение для управления криптопортфелем! 🚀 