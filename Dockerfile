# Использую официальный Python-образ
FROM python:3.12-slim

# Устанавливаю зависимости системы
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Задаю рабочую директорию
WORKDIR /app

# Копирую зависимости
COPY requirements.txt .

# Устанавливаю зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копирую всё приложение
COPY . .

# Применяю миграции и собираю статику при старте контейнера
CMD ["bash", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
