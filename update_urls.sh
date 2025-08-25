#!/bin/bash

# Скрипт для обновления URL в start_app_hybrid.sh
# Использование: ./update_urls.sh [ngrok_url] [serveo_url]

NGROK_URL=${1:-"https://c0bdba71e020.ngrok-free.app"}
SERVEO_URL=${2:-"https://cryptobot-backend.serveo.net"}

echo "🔄 Обновление URL в start_app_hybrid.sh..."
echo "📱 Ngrok URL: $NGROK_URL"
echo "🌐 Serveo URL: $SERVEO_URL"

# Обновляем URL в скрипте
sed -i.bak "s|NGROK_FRONTEND_URL_CONSTANT=\"[^\"]*\"|NGROK_FRONTEND_URL_CONSTANT=\"$NGROK_URL\"|g" start_app_hybrid.sh
sed -i.bak "s|SERVEO_BACKEND_URL_CONSTANT=\"[^\"]*\"|SERVEO_BACKEND_URL_CONSTANT=\"$SERVEO_URL\"|g" start_app_hybrid.sh

echo "✅ URL обновлены!"
echo "💡 Теперь можно запускать: ./start_app_hybrid.sh"
