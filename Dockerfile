FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Создаем директории для базы данных
RUN mkdir -p /app/data

# Открываем порт
EXPOSE 8000

# Команда запуска (будет переопределена в railway.json)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
