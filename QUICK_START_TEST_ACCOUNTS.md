# Быстрый старт с тестовыми аккаунтами

## Запуск backend

```bash
cd backend
docker-compose up -d  # Запустить PostgreSQL и Redis
uvicorn app.main:app --reload
```

При запуске автоматически создадутся 5 тестовых аккаунтов (если `CREATE_TEST_ACCOUNTS=true` в `.env`):

## Тестовые аккаунты

| Роль | Email | Пароль | Доступ |
|------|-------|--------|--------|
| **Admin** | admin@test.com | admin123 | Полный доступ ко всем панелям |
| **Moderator** | moderator@test.com | moderator123 | Модерация контента |
| **Official** | official@test.com | official123 | Работа с проблемами |
| **Volunteer** | volunteer@test.com | volunteer123 | Решение проблем |
| **User** | user@test.com | user123 | Обычный пользователь |

## Вход в систему

### Через frontend (http://localhost:5173)

1. Откройте http://localhost:5173/login
2. Введите email и пароль из таблицы выше
3. Для admin/moderator/official появится иконка Shield в Sidebar
4. Нажмите на Shield → откроется админ-панель

### Через API

```bash
# Логин как admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "admin123"
  }'

# Ответ содержит access_token и refresh_token
```

## Админ-панель

После входа как admin/moderator/official:

1. **Admin Panel** (только admin):
   - Управление пользователями (смена ролей, блокировка)
   - Управление проблемами (отклонение/восстановление)
   - Системная статистика

2. **Moderator Panel** (admin + moderator):
   - Жалобы на комментарии
   - Подозрительные проблемы (низкий truth_score)
   - Верификация новых проблем

3. **Official Panel** (admin + official):
   - Назначенные проблемы
   - Взятие в работу / отметка решённой
   - Официальные комментарии
   - Управляемые зоны

## Отключение тестовых аккаунтов

В продакшене установите в `.env`:

```env
CREATE_TEST_ACCOUNTS=false
```

Или удалите эту переменную — по умолчанию создание отключено.

## Кастомизация

Измените учетные данные в `.env`:

```env
TEST_ADMIN_USERNAME=myadmin
TEST_ADMIN_EMAIL=admin@mycompany.com
TEST_ADMIN_PASSWORD=securepass123
```

Оставьте поля пустыми, чтобы пропустить создание конкретного аккаунта:

```env
TEST_VOLUNTEER_USERNAME=
TEST_VOLUNTEER_EMAIL=
TEST_VOLUNTEER_PASSWORD=
# Volunteer аккаунт не будет создан
```

## Проверка

Проверьте логи при запуске сервера:

```
✅ Created test account: admin (admin@test.com) with role admin
✅ Created test account: moderator (moderator@test.com) with role moderator
✅ Created test account: official (official@test.com) with role official
✅ Created test account: volunteer (volunteer@test.com) with role volunteer
✅ Created test account: testuser (user@test.com) with role user
✅ Test account creation completed
```

Если аккаунт уже существует:

```
Test account admin@test.com already exists, skipping creation
```
