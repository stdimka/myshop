# Базовый образ
FROM python:3.12-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Создаём папки для медиа и статики
RUN mkdir -p /app/media /app/static

# Экспонируем порт
EXPOSE 8000

# Команда запуска (для dev)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
