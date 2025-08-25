#!/bin/bash

# CryptoBook Bot - Остановка приложения
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

# Остановка процессов
stop_processes() {
    print_status "Поиск и остановка процессов CryptoBook Bot..."
    
    # Остановка бекенда (Python процессы)
    BACKEND_PIDS=$(ps aux | grep -E "(python.*main\.py|uvicorn|gunicorn)" | grep -v grep | awk '{print $2}')
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "$BACKEND_PIDS" | xargs kill -9
        print_success "Бекенд остановлен"
    else
        print_warning "Бекенд не найден"
    fi
    
    # Остановка фронтенда (React процессы)
    FRONTEND_PIDS=$(ps aux | grep -E "(react-scripts|npm.*start)" | grep -v grep | awk '{print $2}')
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "$FRONTEND_PIDS" | xargs kill -9
        print_success "Фронтенд остановлен"
    else
        print_warning "Фронтенд не найден"
    fi
    
    # Остановка ngrok
    NGROK_PIDS=$(ps aux | grep "ngrok" | grep -v grep | awk '{print $2}')
    if [ ! -z "$NGROK_PIDS" ]; then
        echo "$NGROK_PIDS" | xargs kill -9
        print_success "ngrok остановлен"
    else
        print_warning "ngrok не найден"
    fi
    
    # Остановка Cloudflare туннелей
    CLOUDFLARE_PIDS=$(ps aux | grep "cloudflared" | grep -v grep | awk '{print $2}')
    if [ ! -z "$CLOUDFLARE_PIDS" ]; then
        echo "$CLOUDFLARE_PIDS" | xargs kill -9
        print_success "Cloudflare туннели остановлены"
    else
        print_warning "Cloudflare туннели не найдены"
    fi
    
    # Остановка Node.js процессов (если остались)
    NODE_PIDS=$(ps aux | grep -E "(node.*start|node.*react)" | grep -v grep | awk '{print $2}')
    if [ ! -z "$NODE_PIDS" ]; then
        echo "$NODE_PIDS" | xargs kill -9
        print_success "Node.js процессы остановлены"
    fi
    
    # Остановка процессов на портах
    PORT_8001_PID=$(lsof -ti:8001 2>/dev/null || true)
    if [ ! -z "$PORT_8001_PID" ]; then
        kill -9 $PORT_8001_PID
        print_success "Процесс на порту 8001 остановлен"
    fi
    
    PORT_3000_PID=$(lsof -ti:3000 2>/dev/null || true)
    if [ ! -z "$PORT_3000_PID" ]; then
        kill -9 $PORT_3000_PID
        print_success "Процесс на порту 3000 остановлен"
    fi
    
    PORT_4040_PID=$(lsof -ti:4040 2>/dev/null || true)
    if [ ! -z "$PORT_4040_PID" ]; then
        kill -9 $PORT_4040_PID
        print_success "Процесс на порту 4040 остановлен"
    fi
}

# Проверка остановки
check_stopped() {
    print_status "Проверка остановки сервисов..."
    
    # Проверка портов
    if lsof -ti:8001 > /dev/null 2>&1; then
        print_warning "Порт 8001 все еще занят"
    else
        print_success "Порт 8001 свободен"
    fi
    
    if lsof -ti:3000 > /dev/null 2>&1; then
        print_warning "Порт 3000 все еще занят"
    else
        print_success "Порт 3000 свободен"
    fi
    
    if lsof -ti:4040 > /dev/null 2>&1; then
        print_warning "Порт 4040 все еще занят"
    else
        print_success "Порт 4040 свободен"
    fi
}

# Принудительная очистка (если обычная остановка не помогла)
force_cleanup() {
    print_status "Принудительная очистка процессов..."
    
    # Убиваем все процессы по портам
    for port in 8001 3000 4040; do
        PIDS=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$PIDS" ]; then
            echo "$PIDS" | xargs kill -9 2>/dev/null || true
            print_success "Процессы на порту $port принудительно остановлены"
        fi
    done
    
    # Убиваем все связанные процессы
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "react-scripts" 2>/dev/null || true
    pkill -f "ngrok" 2>/dev/null || true
    pkill -f "cloudflared" 2>/dev/null || true
    
    print_success "Принудительная очистка завершена"
}

# Главная функция
main() {
    echo "🛑 Остановка CryptoBook Bot..."
    echo "================================"
    
    stop_processes
    check_stopped
    
    # Если порты все еще заняты, используем принудительную очистку
    if lsof -ti:8001 > /dev/null 2>&1 || lsof -ti:3000 > /dev/null 2>&1 || lsof -ti:4040 > /dev/null 2>&1; then
        print_warning "Некоторые процессы не остановились, применяем принудительную очистку..."
        force_cleanup
        check_stopped
    fi
    
    echo ""
    print_success "CryptoBook Bot остановлен!"
    echo "💡 Для запуска используйте: ./start_app.sh"
    echo "💡 Для гибридного режима: ./start_app_hybrid.sh"
}

# Запуск
main "$@" 