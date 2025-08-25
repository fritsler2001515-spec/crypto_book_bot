#!/bin/bash

# CryptoBook Bot - Гибридный запуск (ngrok + Serveo)
# Автор: CryptoBook Bot Team
# Версия: 2.0

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Константы для быстрого доступа к URL
NGROK_FRONTEND_URL_CONSTANT="https://416ae821e74e.ngrok-free.app"
SERVEO_BACKEND_URL_CONSTANT="https://cryptobot-backend.serveo.net"

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
    
    # Проверка SSH (для Serveo)
    if ! command -v ssh &> /dev/null; then
        print_error "SSH не найден!"
        exit 1
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
    # Настройка переменных окружения для работы с туннелями
    export REACT_APP_API_URL="http://localhost:8001/api"
    export DANGEROUSLY_DISABLE_HOST_CHECK=true
    export HOST=0.0.0.0
    export PORT=3000
    npm start &
    FRONTEND_PID=$!
    cd ..
    print_success "Фронтенд запущен (PID: $FRONTEND_PID)"
}

# Запуск гибридных туннелей
start_hybrid_tunnels() {
    print_status "Запуск гибридных туннелей..."
    
    # Ждем готовности сервисов перед запуском туннелей
    print_status "Ожидание готовности сервисов..."
    
    # Ждем бекенд
    for i in {1..30}; do
        if curl -s http://localhost:8001/api/status > /dev/null 2>&1; then
            print_success "Бекенд готов для туннелей!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Бекенд не готов после 30 секунд ожидания!"
            exit 1
        fi
        sleep 1
    done
    
    # Ждем фронтенд
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Фронтенд готов для туннелей!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Фронтенд не готов после 30 секунд ожидания!"
            exit 1
        fi
        sleep 1
    done
    
    # 1. ngrok для фронтенда (прямой запуск без конфига)
    print_status "Запуск ngrok туннеля для фронтенда..."
    ngrok http 3000 &
    NGROK_PID=$!
    
    # Ждем запуска ngrok
    print_status "Ожидание запуска ngrok..."
    sleep 10
    
    # Проверяем, что ngrok запустился
    if ! curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
        print_warning "ngrok не запустился, используем константу"
        NGROK_FRONTEND_URL="$NGROK_FRONTEND_URL_CONSTANT"
    else
        # Получаем ngrok URL для фронтенда
        print_status "Получение ngrok URL для фронтенда..."
        NGROK_FRONTEND_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url' 2>/dev/null)
        
        # Fallback если jq не работает
        if [ -z "$NGROK_FRONTEND_URL" ] || [ "$NGROK_FRONTEND_URL" = "null" ]; then
            print_status "jq не работает, используем grep..."
            NGROK_FRONTEND_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | cut -d'"' -f4 | head -1)
        fi
        
        # Если все еще не получили URL, используем константу
        if [ -z "$NGROK_FRONTEND_URL" ] || [ "$NGROK_FRONTEND_URL" = "null" ]; then
            print_warning "Не удалось получить ngrok URL автоматически, используем константу"
            NGROK_FRONTEND_URL="$NGROK_FRONTEND_URL_CONSTANT"
        fi
    fi
    
    # 2. Serveo для бекенда (используем фиксированный поддомен)
    print_status "Запуск Serveo туннеля для бекенда..."
    
    # Используем фиксированный поддомен для стабильности
    SERVEO_SUBDOMAIN="cryptobot-backend"
    
    print_status "Используем Serveo поддомен: $SERVEO_SUBDOMAIN"
    
    # Запускаем SSH туннель для Serveo
    ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -R $SERVEO_SUBDOMAIN:80:localhost:8001 serveo.net &
    SERVEO_PID=$!
    
    # Ждем установки Serveo соединения
    sleep 5
    
    SERVEO_BACKEND_URL="https://$SERVEO_SUBDOMAIN.serveo.net"
    
    # Проверяем результаты
    if [ -z "$NGROK_FRONTEND_URL" ] || [ "$NGROK_FRONTEND_URL" = "null" ]; then
        print_error "Не удалось получить ngrok URL для фронтенда!"
        exit 1
    fi
    
    print_success "ngrok фронтенд: $NGROK_FRONTEND_URL"
    print_success "Serveo бекенд: $SERVEO_BACKEND_URL"
    
    # Обновляем конфигурацию фронтенда для использования Serveo бекенда
    export REACT_APP_API_URL="$SERVEO_BACKEND_URL/api"
    print_success "Фронтенд настроен на использование Serveo бекенда"
    
    # Обновляем window.__BACKEND_URL__ в index.html
    if [ -f "frontend/public/index.html" ]; then
        sed -i.bak "s|window.__BACKEND_URL__ = '[^']*';|window.__BACKEND_URL__ = '$SERVEO_BACKEND_URL/api';|g" frontend/public/index.html
        print_success "Обновлен window.__BACKEND_URL__ в index.html"
    fi
    
    # Сохраняем URL в файл для использования другими скриптами
    echo "$SERVEO_BACKEND_URL" > .serveo_backend_url
    echo "$NGROK_FRONTEND_URL" > .ngrok_frontend_url
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
    echo "🚀 CryptoBook Bot запущен (ngrok + Serveo режим)!"
    echo "============================================="
    echo "📱 Telegram Bot: Работает"
    echo "🌐 Backend API (Serveo): $SERVEO_BACKEND_URL"
    echo "🎨 Frontend (ngrok): $NGROK_FRONTEND_URL"
    echo "🔗 Backend (локальный): http://localhost:8001"
    echo "🔗 Frontend (локальный): http://localhost:3000"
    echo ""
    echo "📊 API Documentation: $SERVEO_BACKEND_URL/docs"
    echo "📋 Swagger UI: $SERVEO_BACKEND_URL/docs"
    echo "🔍 ngrok Dashboard: http://localhost:4040"
    echo ""
    echo "💡 Для остановки нажмите Ctrl+C"
    echo ""
}

# Очистка при выходе
cleanup() {
    print_status "Остановка сервисов..."
    
    # Останавливаем процессы по PID
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
    
    if [ ! -z "$SERVEO_PID" ]; then
        kill $SERVEO_PID 2>/dev/null || true
        print_success "Serveo туннель остановлен"
    fi
    
    # Дополнительная очистка по портам
    print_status "Очистка процессов по портам..."
    
    # Останавливаем процессы на порту 8001 (бекенд)
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    
    # Останавливаем процессы на порту 3000 (фронтенд)
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    # Останавливаем процессы на порту 4040 (ngrok)
    lsof -ti:4040 | xargs kill -9 2>/dev/null || true
    
    # Останавливаем все SSH туннели к serveo.net
    pkill -f "serveo.net" 2>/dev/null || true
    
    # Очистка временных файлов
    rm -f .serveo_backend_url .ngrok_frontend_url
    
    print_success "Все сервисы остановлены!"
    exit 0
}

# Функция для получения нового ngrok URL
get_new_ngrok_url() {
    print_status "Получение нового ngrok URL..."
    
    # Запускаем ngrok временно
    ngrok http 3000 &
    local temp_ngrok_pid=$!
    
    # Ждем запуска
    sleep 10
    
    # Получаем URL
    local new_url=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url' 2>/dev/null)
    
    # Останавливаем временный ngrok
    kill $temp_ngrok_pid 2>/dev/null || true
    
    if [ ! -z "$new_url" ] && [ "$new_url" != "null" ]; then
        print_success "Новый ngrok URL: $new_url"
        echo "$new_url"
    else
        print_error "Не удалось получить новый ngrok URL"
        echo ""
    fi
}

# Обработка сигналов
trap cleanup SIGINT SIGTERM

# Главная функция
main() {
    # Проверяем аргументы
    if [ "$1" = "--new-ngrok-url" ]; then
        echo "🔄 Получение нового ngrok URL..."
        echo "============================================="
        get_new_ngrok_url
        exit 0
    fi
    
    echo "🚀 Запуск CryptoBook Bot (ngrok + Serveo режим)..."
    echo "============================================="
    echo "🌐 Frontend: ngrok"
    echo "🌐 Backend: Serveo"
    echo "============================================="
    
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
    start_hybrid_tunnels
    
    # Ожидание
    wait_for_services
    
    # Показ информации
    show_info
    
    # Ожидание
    wait
}

# Запуск
main "$@"
