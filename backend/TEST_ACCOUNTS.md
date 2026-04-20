# Test Accounts Auto-Creation

Система автоматического создания тестовых аккаунтов для разработки.

## Конфигурация

В `.env` добавлены следующие переменные:

```env
# Флаг включения/выключения автоматического создания
CREATE_TEST_ACCOUNTS=true

# Учетные данные для каждой роли
TEST_ADMIN_USERNAME=admin
TEST_ADMIN_EMAIL=admin@test.com
TEST_ADMIN_PASSWORD=admin123

TEST_MODERATOR_USERNAME=moderator
TEST_MODERATOR_EMAIL=moderator@test.com
TEST_MODERATOR_PASSWORD=moderator123

TEST_OFFICIAL_USERNAME=official
TEST_OFFICIAL_EMAIL=official@test.com
TEST_OFFICIAL_PASSWORD=official123

TEST_VOLUNTEER_USERNAME=volunteer
TEST_VOLUNTEER_EMAIL=volunteer@test.com
TEST_VOLUNTEER_PASSWORD=volunteer123

TEST_USER_USERNAME=testuser
TEST_USER_EMAIL=user@test.com
TEST_USER_PASSWORD=user123
```

## Как это работает

1. При запуске сервера в `lifespan` вызывается `create_all_test_accounts()`
2. Функция проверяет флаг `CREATE_TEST_ACCOUNTS`
3. Для каждой роли проверяет наличие учетных данных в `.env`
4. Если данные есть и пользователь не существует — создает аккаунт
5. Если данные отсутствуют или пользователь уже существует — пропускает

## Особенности

- **Безопасность**: Аккаунты создаются только если `CREATE_TEST_ACCOUNTS=true`
- **Идемпотентность**: Повторный запуск не создаст дубликаты
- **Гибкость**: Можно создать только нужные аккаунты, оставив остальные пустыми
- **Логирование**: Все действия логируются для отладки

## Созданные аккаунты

Каждый тестовый аккаунт получает:
- Соответствующую роль (admin, moderator, official, volunteer, user)
- Репутацию 100.0
- Статус `is_verified=True`
- Город: Bishkek, Страна: Kyrgyzstan

## Отключение в продакшене

**ВАЖНО**: В продакшене установите `CREATE_TEST_ACCOUNTS=false` или удалите эту переменную из `.env`

## Использование

После запуска сервера можно войти с любым из тестовых аккаунтов:

```bash
# Логин как admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "admin123"}'

# Логин как moderator
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "moderator@test.com", "password": "moderator123"}'
```

## Файлы

- `app/utils/create_test_accounts.py` — логика создания аккаунтов
- `app/config.py` — конфигурация переменных окружения
- `app/main.py` — интеграция в lifespan
- `.env` — учетные данные тестовых аккаунтов
