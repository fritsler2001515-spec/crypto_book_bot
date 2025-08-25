#!/bin/bash

# Скрипт для получения нового ngrok URL
# Автор: CryptoBook Bot Team

echo "🔄 Получение нового ngrok URL..."

# Запускаем ngrok временно
ngrok http 3000 --log=stdout > /dev/null 2>&1 &
NGROK_PID=$!

# Ждем запуска
sleep 5

# Получаем URL
NEW_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url' 2>/dev/null)

# Останавливаем ngrok
kill $NGROK_PID 2>/dev/null || true

if [ ! -z "$NEW_URL" ] && [ "$NEW_URL" != "null" ]; then
    echo "✅ Новый ngrok URL: $NEW_URL"
    echo ""
    echo "📝 Для обновления в скрипте замените строку:"
    echo "NGROK_FRONTEND_URL_CONSTANT=\"https://b071661f1106.ngrok-free.app\""
    echo "на:"
    echo "NGROK_FRONTEND_URL_CONSTANT=\"$NEW_URL\""
else
    echo "❌ Не удалось получить новый ngrok URL"
fi
