# =========================
# 1️⃣ Builder
# =========================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Теперь копируем код
COPY . /app

# ВАЖНО: если collectstatic зависит от env,
# можно задать временные значения
ENV DJANGO_SETTINGS_MODULE=src.settings.production
ENV DEBUG=False

RUN python manage.py collectstatic --noinput


# =========================
# 2️⃣ Runtime
# =========================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY --from=builder /app /app

RUN addgroup --system django && adduser --system --ingroup django django
RUN chown -R django:django /app

COPY compose/production/django/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh && chown django:django /app/entrypoint.sh

USER django

ENTRYPOINT ["/app/entrypoint.sh"]