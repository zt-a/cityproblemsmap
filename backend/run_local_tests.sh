#!/bin/bash
# run_local_tests.sh - Скрипт для запуска тестов локально

# Установить переменные окружения для локального запуска
export LOCAL_DATABASE=true
export TESTING=true
export LOCAL_DATABASE_URL="postgresql://postgres:supersecret@localhost:5433/city_problems"
export TEST_DATABASE_URL="postgresql://postgres:supersecret@localhost:5433/city_problems_test"
export LOCAL_REDIS_URL="redis://localhost:6379/0"
export TEST_REDIS_URL="redis://localhost:6379/1"

# Активировать venv
source venv/bin/activate

# Запустить тесты
docker exec -it city_db psql -U postgres -c "DROP DATABASE IF EXISTS city_problems_test;"
docker exec -it city_db psql -U postgres -c "CREATE DATABASE city_problems_test;"
pytest "$@"
