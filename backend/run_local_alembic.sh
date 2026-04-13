#!/bin/bash
# run_local_alembic.sh - Скрипт для запуска Alembic локально

# Установить переменные окружения для локального запуска
export LOCAL_DATABASE=true
export LOCAL_DATABASE_URL="postgresql://postgres:supersecret@localhost:5433/city_problems"
export TEST_DATABASE_URL="postgresql://postgres:supersecret@localhost:5433/city_problems_test"

# Активировать venv
source venv/bin/activate

# Запустить alembic с переданными аргументами
alembic "$@"
