FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN pip install --upgrade pip

# Копируем requirements
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Код будет монтироваться через volumes
CMD ["celery", "-A", "src", "worker", "--loglevel=INFO"]