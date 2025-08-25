FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Открываем порт
EXPOSE 8001

# Запускаем приложение
CMD ["python", "main.py"]
