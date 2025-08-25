#!/bin/bash

# CryptoBook Bot - Локальный запуск (без туннелей)
# Для разработки и тестирования

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

# Функция завершения процессов на портах
kill_processes_on_ports() {
    print_status "Завершение процессов на портах 8001 и 3000..."
    
    # Завершаем процессы на порту 8001 (бэкенд)
    local backend_pids=$(lsof -ti:8001 2>/dev/null || true)
    if [ ! -z "$backend_pids" ]; then
        echo "$backend_pids" | xargs kill -9 2>/dev/null || true
        print_success "Процессы на порту 8001 завершены"
    else
        print_status "Порт 8001 свободен"
    fi
    
    # Завершаем процессы на порту 3000 (фронтенд)
    local frontend_pids=$(lsof -ti:3000 2>/dev/null || true)
    if [ ! -z "$frontend_pids" ]; then
        echo "$frontend_pids" | xargs kill -9 2>/dev/null || true
        print_success "Процессы на порту 3000 завершены"
    else
        print_status "Порт 3000 свободен"
    fi
    
    # Ждем освобождения портов
    sleep 2
}

# Функция очистки при выходе
cleanup() {
    print_status "Останавливаем процессы..."
    
    # Останавливаем бекенд
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_success "Бекенд остановлен"
    fi
    
    # Останавливаем фронтенд
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Фронтенд остановлен"
    fi
    
    # Очищаем временные файлы
    rm -f .local_backend_url .local_frontend_url
    
    print_success "Очистка завершена"
    exit 0
}

# Устанавливаем обработчик сигналов
trap cleanup SIGINT SIGTERM

echo "🚀 Запуск CryptoBook Bot (локальный режим)..."
echo "================================================"

# Проверяем, что мы в корневой директории проекта
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Завершаем процессы на портах перед запуском
kill_processes_on_ports

# Проверяем наличие виртуального окружения
if [ ! -d "backend/venv" ]; then
    print_error "Виртуальное окружение не найдено. Создайте его: cd backend && python -m venv venv"
    exit 1
fi

# Активируем виртуальное окружение
print_status "Активация виртуального окружения..."
source backend/venv/bin/activate

# Проверяем зависимости бекенда
print_status "Проверка зависимостей бекенда..."
cd backend
if [ ! -f "requirements.txt" ]; then
    print_error "Файл requirements.txt не найден в backend/"
    exit 1
fi

# Устанавливаем зависимости если нужно
if ! python -c "import fastapi, aiogram, sqlalchemy" 2>/dev/null; then
    print_status "Установка зависимостей бекенда..."
    pip install -r requirements.txt
fi

# Проверяем зависимости фронтенда
print_status "Проверка зависимостей фронтенда..."
cd ../frontend
if [ ! -f "package.json" ]; then
    print_error "Файл package.json не найден в frontend/"
    exit 1
fi

# Устанавливаем зависимости если нужно
if [ ! -d "node_modules" ]; then
    print_status "Установка зависимостей фронтенда..."
    npm install
fi

cd ..

# Проверяем базу данных
print_status "Проверка базы данных..."
cd backend
python scripts/init_db.py
cd ..

# Запускаем бекенд
print_status "Запуск бекенда..."
cd backend
# Запускаем через main.py, который содержит и FastAPI, и Telegram бота
python main.py &
BACKEND_PID=$!
cd ..

# Ждем запуска бекенда
print_status "Ожидание запуска бекенда..."
sleep 8

# Проверяем, что бекенд запустился
if ! curl -s http://localhost:8001/api/status > /dev/null; then
    print_error "Бекенд не запустился"
    cleanup
    exit 1
fi

print_success "Бекенд запущен на http://localhost:8001"

# Сохраняем URL бекенда
echo "http://localhost:8001" > .local_backend_url

# Настраиваем фронтенд для работы с локальным бекендом
print_status "Настройка фронтенда..."
cd frontend

# Обновляем конфигурацию фронтенда
export REACT_APP_API_URL="http://localhost:8001/api"
print_success "Фронтенд настроен на использование локального бекенда"

# Обновляем index.html если нужно
if [ -f "public/index.html" ]; then
    sed -i.bak "s|window.__BACKEND_URL__ = '[^']*';|window.__BACKEND_URL__ = 'http://localhost:8001/api';|g" public/index.html
fi

# Запускаем фронтенд
print_status "Запуск фронтенда..."
npm start &
FRONTEND_PID=$!
cd ..

# Ждем запуска фронтенда
print_status "Ожидание запуска фронтенда..."
sleep 15

# Проверяем, что фронтенд запустился
if ! curl -s http://localhost:3000 > /dev/null; then
    print_error "Фронтенд не запустился"
    cleanup
    exit 1
fi

print_success "Фронтенд запущен на http://localhost:3000"

# Сохраняем URL фронтенда
echo "http://localhost:3000" > .local_frontend_url

echo ""
echo "🎉 CryptoBook Bot запущен (локальный режим)!"
echo "================================================"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001"
echo "📊 API Documentation: http://localhost:8001/docs"
echo "📋 Swagger UI: http://localhost:8001/docs"
echo "🤖 Telegram Bot: Запущен и работает"
echo ""
echo "💡 Для остановки нажмите Ctrl+C"
echo ""

# Ждем завершения
wait
