# =========================
# 1️⃣ Builder stage
# =========================
FROM python:3.11-slim AS builder

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

# Устанавливаем зависимости в отдельную директорию
RUN pip install --prefix=/install -r requirements.txt


# =========================
# 2️⃣ Runtime stage
# =========================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Только runtime-зависимости
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Копируем установленные пакеты
COPY --from=builder /install /usr/local

# Создаем пользователя
RUN addgroup --system django && adduser --system --ingroup django django

# Копируем проект
COPY . /app

# Права
RUN chown -R django:django /app

USER django

# По умолчанию команда будет переопределена в docker-compose
CMD ["celery", "-A", "src", "worker", "--loglevel=INFO"]