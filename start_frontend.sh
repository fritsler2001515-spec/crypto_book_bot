#!/bin/bash

# CryptoBook Bot - Запуск только фронтенда
# Для разработки UI

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

# Функция очистки при выходе
cleanup() {
    print_status "Останавливаем фронтенд..."
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Фронтенд остановлен"
    fi
    
    rm -f .local_frontend_url
    print_success "Очистка завершена"
    exit 0
}

# Устанавливаем обработчик сигналов
trap cleanup SIGINT SIGTERM

echo "🌐 Запуск CryptoBook Bot Frontend..."
echo "===================================="

# Проверяем, что мы в корневой директории проекта
if [ ! -f "README.md" ] || [ ! -d "frontend" ]; then
    print_error "Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Проверяем зависимости фронтенда
print_status "Проверка зависимостей фронтенда..."
cd frontend
if [ ! -f "package.json" ]; then
    print_error "Файл package.json не найден в frontend/"
    exit 1
fi

# Устанавливаем зависимости если нужно
if [ ! -d "node_modules" ]; then
    print_status "Установка зависимостей фронтенда..."
    npm install
fi

# Настраиваем фронтенд для работы с локальным бекендом
print_status "Настройка фронтенда..."

# Проверяем, есть ли URL бекенда
if [ -f "../.local_backend_url" ]; then
    BACKEND_URL=$(cat ../.local_backend_url)
    print_success "Найден URL бекенда: $BACKEND_URL"
else
    print_warning "URL бекенда не найден. Используем localhost:8001"
    BACKEND_URL="http://localhost:8001"
fi

# Обновляем конфигурацию фронтенда
export REACT_APP_API_URL="$BACKEND_URL/api"
print_success "Фронтенд настроен на использование бекенда: $BACKEND_URL"

# Обновляем index.html
sed -i.bak "s|window.__BACKEND_URL__ = '[^']*';|window.__BACKEND_URL__ = '$BACKEND_URL/api';|g" public/index.html

# Запускаем фронтенд
print_status "Запуск фронтенда..."
npm start &
FRONTEND_PID=$!

# Ждем запуска фронтенда
print_status "Ожидание запуска фронтенда..."
sleep 10

# Проверяем, что фронтенд запустился
if ! curl -s http://localhost:3000 > /dev/null; then
    print_error "Фронтенд не запустился"
    cleanup
    exit 1
fi

print_success "Фронтенд запущен на http://localhost:3000"

# Сохраняем URL фронтенда
cd ..
echo "http://localhost:3000" > .local_frontend_url

echo ""
echo "🎉 CryptoBook Bot Frontend запущен!"
echo "===================================="
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: $BACKEND_URL"
echo ""
echo "💡 Для остановки нажмите Ctrl+C"
echo ""

# Ждем завершения
wait
