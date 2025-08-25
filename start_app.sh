#!/bin/bash

# CryptoBook Bot - Запуск приложения
# Автор: CryptoBook Bot Team
# Версия: 1.0

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка зависимостей
check_dependencies() {
    print_status "Проверка зависимостей..."
    
    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 не найден!"
        exit 1
    fi
    
    # Проверка Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js не найден!"
        exit 1
    fi
    
    # Проверка ngrok
    if ! command -v ngrok &> /dev/null; then
        print_warning "ngrok не найден. Устанавливаем..."
        brew install ngrok
    fi
    
    # Проверка PostgreSQL
    if ! pg_isready -h 127.0.0.1 -p 5432 &> /dev/null; then
        print_error "PostgreSQL не запущен! Запустите PostgreSQL и попробуйте снова."
        exit 1
    fi
    
    print_success "Все зависимости найдены!"
}

# Активация виртуального окружения
activate_venv() {
    print_status "Активация виртуального окружения..."
    
    if [ ! -d ".venv" ]; then
        print_error "Виртуальное окружение не найдено!"
        exit 1
    fi
    
    source .venv/bin/activate
    print_success "Виртуальное окружение активировано!"
}

# Установка зависимостей бекенда
install_backend_deps() {
    print_status "Установка зависимостей бекенда..."
    pip install -r backend/requirements.txt
    print_success "Зависимости бекенда установлены!"
}

# Установка зависимостей фронтенда
install_frontend_deps() {
    print_status "Установка зависимостей фронтенда..."
    cd frontend
    npm install
    cd ..
    print_success "Зависимости фронтенда установлены!"
}

# Проверка базы данных
check_database() {
    print_status "Проверка базы данных..."
    cd backend
    python scripts/init_db.py
    cd ..
    print_success "База данных готова!"
}

# Запуск бекенда
start_backend() {
    print_status "Запуск бекенда..."
    cd backend
    python main.py &
    BACKEND_PID=$!
    cd ..
    print_success "Бекенд запущен (PID: $BACKEND_PID)"
}

# Запуск фронтенда
start_frontend() {
    print_status "Запуск фронтенда..."
    cd frontend
    # Устанавливаем переменную окружения для API
    # В Telegram Web App будем использовать ngrok URL
    export REACT_APP_API_URL="http://localhost:8001/api"
    npm start &
    FRONTEND_PID=$!
    cd ..
    print_success "Фронтенд запущен (PID: $FRONTEND_PID)"
}

# Запуск туннелей (ngrok + serveo)
start_tunnels() {
    print_status "Запуск туннелей (ngrok + serveo)..."
    
    # Запускаем ngrok для фронтенда
    ngrok http 3000 > /dev/null 2>&1 &
    NGROK_PID=$!
    
    # Ждем запуска ngrok
    sleep 5
    
    # Получаем ngrok URL для фронтенда
    print_status "Получение ngrok URL..."
    
    # Пробуем с jq
    NGROK_FRONTEND_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url' 2>/dev/null)
    
    # Fallback если jq не установлен или не работает
    if [ -z "$NGROK_FRONTEND_URL" ] || [ "$NGROK_FRONTEND_URL" = "null" ]; then
        print_status "jq не работает, используем grep..."
        NGROK_FRONTEND_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | cut -d'"' -f4 | head -1)
    fi
    
    # Проверяем результат
    if [ -z "$NGROK_FRONTEND_URL" ] || [ "$NGROK_FRONTEND_URL" = "null" ]; then
        print_error "Не удалось получить ngrok URL!"
        print_error "Проверьте, что ngrok запущен: curl http://localhost:4040/api/tunnels"
        exit 1
    fi
    
    print_success "Получен ngrok URL: $NGROK_FRONTEND_URL"
    
    print_success "ngrok фронтенд: $NGROK_FRONTEND_URL"
    print_success "бэкенд: http://localhost:8001 (локальный)"
    
    # Оставляем бэкенд локальным, используем прокси в React
    if [ -f "frontend/public/index.html" ]; then
        sed -i.bak "s|window.__BACKEND_URL__ = '/api';|window.__BACKEND_URL__ = '/api';|g" frontend/public/index.html
        print_success "Бэкенд остается локальным, используем прокси"
    fi
}

# Ожидание запуска сервисов
wait_for_services() {
    print_status "Ожидание запуска сервисов..."
    
    # Ждем бекенд
    for i in {1..30}; do
        if curl -s http://localhost:8001/api/status > /dev/null 2>&1; then
            print_success "Бекенд готов!"
            break
        fi
        sleep 1
    done
    
    # Ждем фронтенд
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Фронтенд готов!"
            break
        fi
        sleep 1
    done
}

# Вывод информации
show_info() {
    echo ""
    echo "🚀 CryptoBook Bot запущен!"
    echo "=================================="
    echo "📱 Telegram Bot: Работает"
echo "🌐 Backend API: http://localhost:8001"
echo "🎨 Frontend: http://localhost:3000"
echo "🔗 Public URL (Frontend): $NGROK_FRONTEND_URL"
echo "🔗 Backend: http://localhost:8001 (локальный)"
    echo ""
    echo "📊 API Documentation: http://localhost:8001/docs"
    echo "📋 Swagger UI: http://localhost:8001/docs"
    echo ""
    echo "💡 Для остановки нажмите Ctrl+C"
    echo ""
}

# Очистка при выходе
cleanup() {
    print_status "Остановка сервисов..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_success "Бекенд остановлен"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Фронтенд остановлен"
    fi
    
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null || true
        print_success "ngrok остановлен"
    fi
    
    # serveo больше не используется
    
    print_success "Все сервисы остановлены!"
    exit 0
}

# Обработка сигналов
trap cleanup SIGINT SIGTERM

# Главная функция
main() {
    echo "🚀 Запуск CryptoBook Bot..."
    echo "================================"
    
    # Проверки
    check_dependencies
    activate_venv
    
    # Установка зависимостей (если нужно)
    if [ "$1" = "--install" ]; then
        install_backend_deps
        install_frontend_deps
    fi
    
    # Проверка БД
    check_database
    
    # Запуск сервисов
    start_backend
    start_frontend
    start_tunnels
    
    # Ожидание
    wait_for_services
    
    # Показ информации
    show_info
    
    # Ожидание
    wait
}

# Запуск
main "$@" 