FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt из backend
COPY backend/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь backend код
COPY backend/ .

# Открываем порт
EXPOSE 8001

# Запускаем приложение
CMD ["python", "main.py"]
