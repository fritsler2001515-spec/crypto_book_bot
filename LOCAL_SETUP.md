# 🚀 Локальный запуск CryptoBook Bot

Это руководство поможет вам запустить CryptoBook Bot локально для разработки и тестирования.

## 📋 Предварительные требования

### 1. Системные требования
- **Python 3.8+**
- **Node.js 16+**
- **PostgreSQL 12+**
- **Git**

### 2. Установка PostgreSQL

#### macOS (с Homebrew):
```bash
brew install postgresql
brew services start postgresql
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Windows:
Скачайте и установите с [официального сайта](https://www.postgresql.org/download/windows/)

### 3. Настройка базы данных
```bash
# Подключаемся к PostgreSQL
sudo -u postgres psql

# Создаем пользователя и базу данных
CREATE USER postgres WITH PASSWORD 'user123';
CREATE DATABASE postgres OWNER postgres;
GRANT ALL PRIVILEGES ON DATABASE postgres TO postgres;
\q
```

## 🔧 Быстрая настройка

### 1. Автоматическая настройка
```bash
# Запустите скрипт настройки
./setup_local.sh
```

### 2. Ручная настройка

#### Создание виртуального окружения:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

#### Установка зависимостей:
```bash
# Бекенд
cd backend
pip install -r requirements.txt

# Фронтенд
cd ../frontend
npm install
```

## ⚙️ Конфигурация

### 1. Создание файла .env
Создайте файл `backend/.env` со следующим содержимым:

```env
# Telegram Bot Token (замените на ваш токен)
BOT_TOKEN=your_telegram_bot_token_here

# Database (PostgreSQL)
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASS=user123

# API Settings
API_HOST=0.0.0.0
API_PORT=8001

# Web App URL (для локального запуска)
WEBAPP_URL=http://localhost:3000

# Chat IDs (опционально, для уведомлений)
CHAT_IDS=
```

### 2. Получение Telegram Bot Token

1. Напишите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `backend/.env`

## 🚀 Запуск

### Автоматический запуск
```bash
./start_local.sh
```

### Ручной запуск

#### 1. Запуск бекенда:
```bash
cd backend
source venv/bin/activate
python main.py
```

#### 2. Запуск фронтенда (в новом терминале):
```bash
cd frontend
npm start
```

## 🌐 Доступные URL

После запуска будут доступны:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Swagger UI**: http://localhost:8001/docs

## 📱 Telegram Bot

Бот будет доступен в Telegram и поддерживает следующие команды:

- `/start` - Начать работу с ботом
- `/webapp` - Получить ссылку на веб-приложение
- `/app` - Открыть веб-приложение

## 🔍 Отладка

### Проверка статуса бекенда:
```bash
curl http://localhost:8001/api/status
```

### Проверка базы данных:
```bash
cd backend
source venv/bin/activate
python scripts/init_db.py
```

### Логи бекенда:
Логи выводятся в консоль при запуске `python main.py`

### Логи фронтенда:
Логи выводятся в консоль при запуске `npm start`

## 🛠️ Разработка

### Структура проекта:
```
crypto_book_bot/
├── backend/                 # Python FastAPI + Telegram Bot
│   ├── domain/             # Бизнес-логика
│   ├── infrastructure/     # База данных и внешние API
│   ├── presentation/       # API endpoints и Telegram handlers
│   └── shared/             # Общие компоненты
├── frontend/               # React приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── pages/          # Страницы приложения
│   │   └── services/       # API клиенты
│   └── public/             # Статические файлы
└── scripts/                # Скрипты запуска
```

### Основные технологии:
- **Backend**: FastAPI, SQLAlchemy, aiogram, PostgreSQL
- **Frontend**: React, TypeScript, Material-UI
- **External APIs**: CoinGecko API

## 🐛 Устранение неполадок

### Проблема: "Бекенд не запустился"
**Решение:**
1. Проверьте, что PostgreSQL запущен
2. Убедитесь, что файл `.env` создан и настроен
3. Проверьте логи в консоли

### Проблема: "Фронтенд не запустился"
**Решение:**
1. Убедитесь, что Node.js установлен
2. Проверьте, что `npm install` выполнен
3. Проверьте логи в консоли

### Проблема: "Ошибка подключения к базе данных"
**Решение:**
1. Убедитесь, что PostgreSQL запущен
2. Проверьте настройки в `.env`
3. Проверьте права доступа пользователя

### Проблема: "Telegram Bot не отвечает"
**Решение:**
1. Проверьте токен бота в `.env`
2. Убедитесь, что бот не заблокирован
3. Проверьте логи бекенда

## 📞 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи в консоли
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки в файле `.env`
4. Убедитесь, что PostgreSQL запущен и доступен

## 🔄 Обновление

Для обновления проекта:

```bash
# Обновить код
git pull

# Обновить зависимости бекенда
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Обновить зависимости фронтенда
cd ../frontend
npm install

# Перезапустить приложение
./start_local.sh
```
