#!/bin/bash

# Скрипт для инициализации и запуска backend приложения

echo "Waiting for PostgreSQL..."
while ! pg_isready -h postgres -U postgres > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

