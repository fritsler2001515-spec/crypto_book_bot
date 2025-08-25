#!/bin/bash

# CryptoBook Bot - Настройка локального окружения
# Создает необходимые файлы и настройки для локального запуска

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🔧 Настройка локального окружения CryptoBook Bot..."
echo "================================================"

# Проверяем, что мы в корневой директории проекта
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Создаем виртуальное окружение для бекенда
print_status "Настройка виртуального окружения..."
cd backend

if [ ! -d "venv" ]; then
    print_status "Создание виртуального окружения..."
    python3 -m venv venv
    print_success "Виртуальное окружение создано"
else
    print_success "Виртуальное окружение уже существует"
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости бекенда
print_status "Установка зависимостей бекенда..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Зависимости бекенда установлены"
else
    print_error "Файл requirements.txt не найден"
    exit 1
fi

cd ..

# Устанавливаем зависимости фронтенда
print_status "Установка зависимостей фронтенда..."
cd frontend

if [ -f "package.json" ]; then
    if [ ! -d "node_modules" ]; then
        npm install
        print_success "Зависимости фронтенда установлены"
    else
        print_success "Зависимости фронтенда уже установлены"
    fi
else
    print_error "Файл package.json не найден"
    exit 1
fi

cd ..

# Создаем файл .env если его нет
print_status "Проверка файла .env..."
if [ ! -f "backend/.env" ]; then
    print_warning "Файл .env не найден. Создайте его вручную в папке backend/"
    echo ""
    echo "Пример содержимого backend/.env:"
    echo "=================================="
    echo "# Telegram Bot Token (замените на ваш токен)"
    echo "BOT_TOKEN=your_telegram_bot_token_here"
    echo ""
    echo "# Database (PostgreSQL)"
    echo "DB_HOST=127.0.0.1"
    echo "DB_PORT=5432"
    echo "DB_NAME=postgres"
    echo "DB_USER=postgres"
    echo "DB_PASS=user123"
    echo ""
    echo "# API Settings"
    echo "API_HOST=0.0.0.0"
    echo "API_PORT=8001"
    echo ""
    echo "# Web App URL (для локального запуска)"
    echo "WEBAPP_URL=http://localhost:3000"
    echo ""
    echo "# Chat IDs (опционально, для уведомлений)"
    echo "CHAT_IDS="
    echo ""
else
    print_success "Файл .env найден"
fi

# Проверяем базу данных
print_status "Проверка базы данных..."
cd backend
source venv/bin/activate

if python scripts/init_db.py; then
    print_success "База данных настроена"
else
    print_warning "Ошибка при настройке базы данных. Убедитесь, что PostgreSQL запущен"
fi

cd ..

echo ""
echo "🎉 Настройка завершена!"
echo "================================================"
echo ""
echo "📋 Следующие шаги:"
echo "1. Создайте файл backend/.env с вашими настройками"
echo "2. Убедитесь, что PostgreSQL запущен"
echo "3. Запустите: ./start_local.sh"
echo ""
echo "💡 Для получения Telegram Bot Token:"
echo "   - Напишите @BotFather в Telegram"
echo "   - Создайте нового бота: /newbot"
echo "   - Скопируйте токен в backend/.env"
echo ""

