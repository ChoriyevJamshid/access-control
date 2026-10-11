#!/bin/bash
set -e

echo "🔄 Ожидание PostgreSQL..."
until pg_isready -h db -p 5432; do
  sleep 1
done
echo "✅ PostgreSQL доступен"

echo "🔄 Ожидание PgBouncer..."
until nc -z pgbouncer ${PGBOUNCER_PORT}; do
  sleep 1
done
echo "✅ PgBouncer доступен"

echo "📦 Применение миграций..."
python manage.py migrate --noinput

echo "🚀 Запуск Gunicorn..."

exec gunicorn src.wsgi:application \
    --bind 0.0.0.0:${DJANGO_PORT} \
    --workers $((2 * $(nproc) + 1)) \
    --threads 2 \
    --worker-class gthread \
    --access-logfile - \
    --error-logfile - \
    --log-level info