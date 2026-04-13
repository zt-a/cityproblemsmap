# CityProblemMap — Полная документация проекта

> Дата обновления: 2026-04-09

---

## 📋 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Запуск локально и в Docker](#запуск-локально-и-в-docker)
3. [API документация](#api-документация)
4. [Roadmap развития](#roadmap-развития)

---

# Быстрый старт

## Docker (рекомендуется)

```bash
# Запуск
docker compose up -d

# Тесты
docker compose exec api pytest tests/test_moderator.py tests/test_official.py -v

# API доступен на http://localhost:8000
# Swagger: http://localhost:8000/docs
```

## Локально (для разработки)

```bash
# 1. Запустить БД и Redis
docker compose up db redis -d

# 2. Установить зависимости (первый раз)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Запустить тесты
./run_local_tests.sh

# 4. Запустить Alembic
./run_local_alembic.sh current

# 5. Запустить API
source venv/bin/activate
export LOCAL_DATABASE=true
uvicorn app.main:app --reload
```

## ✅ Проверено

- ✅ Alembic работает локально и в Docker
- ✅ Тесты проходят локально и в Docker (10/10)
- ✅ API запускается локально и в Docker
- ✅ 15 новых эндпоинтов (moderator + official)

---

# Запуск локально и в Docker

Проект настроен для работы в двух режимах: локально и в Docker. Переключение происходит автоматически через переменные окружения.

## 🐳 Запуск в Docker (по умолчанию)

### Настройка .env для Docker
```bash
# Database
DATABASE_URL=postgresql://postgres:supersecret@db:5432/city_problems
TEST_DATABASE_URL=postgresql://postgres:supersecret@db:5432/city_problems_test
LOCAL_DATABASE=false

# Redis
REDIS_URL=redis://redis:6379/0
TEST_REDIS_URL=redis://redis:6379/1

# Testing
TESTING=true  # для тестов в Docker
```

### Команды Docker
```bash
# Запуск всех сервисов
docker compose up -d

# Просмотр логов
docker compose logs -f api

# Остановка
docker compose down

# Пересборка после изменений
docker compose up -d --build

# Запуск тестов в Docker
docker compose exec api pytest tests/ -v

# Миграции в Docker
docker compose exec api alembic upgrade head
docker compose exec api alembic revision --autogenerate -m "description"
```

---

## 💻 Запуск локально

### 1. Настройка .env для локального запуска
```bash
# Database - локальные порты
LOCAL_DATABASE_URL=postgresql://postgres:supersecret@localhost:5433/city_problems
TEST_DATABASE_URL=postgresql://postgres:supersecret@localhost:5433/city_problems_test
LOCAL_DATABASE=true  # ← ВАЖНО! Включает локальный режим

# Redis - локальные порты
LOCAL_REDIS_URL=redis://localhost:6379/0
TEST_REDIS_URL=redis://localhost:6379/1

# Testing
TESTING=true  # для тестов
```

### 2. Запуск зависимостей (PostgreSQL + Redis)
```bash
# Запускаем только БД и Redis через Docker
docker compose up db redis -d

# Проверяем что работают
docker compose ps
```

### 3. Установка зависимостей Python
```bash
# Создаём виртуальное окружение
python -m venv venv

# Активируем
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 4. Запуск API локально
```bash
# Активируем venv
source venv/bin/activate

# Запускаем сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Запуск тестов локально
```bash
# Активируем venv
source venv/bin/activate

# Запускаем все тесты
pytest tests/ -v

# Запускаем конкретный файл
pytest tests/test_moderator.py -v

# С покрытием
pytest tests/ --cov=app --cov-report=html
```

### 6. Миграции локально
```bash
# Активируем venv
source venv/bin/activate

# Применить миграции
alembic upgrade head

# Создать новую миграцию
alembic revision --autogenerate -m "add new field"

# Откатить миграцию
alembic downgrade -1
```

### 7. Celery локально
```bash
# Активируем venv
source venv/bin/activate

# Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Celery beat (в отдельном терминале)
celery -A app.workers.celery_app beat --loglevel=info
```

---

## 🔄 Как работает автоматическое переключение

### config.py автоматически выбирает правильные URL:

```python
@property
def db_url(self) -> str:
    """
    - TESTING=true → TEST_DATABASE_URL
    - LOCAL_DATABASE=true → LOCAL_DATABASE_URL
    - иначе → DATABASE_URL (docker)
    """
    if self.TESTING and self.TEST_DATABASE_URL:
        return self.TEST_DATABASE_URL
    
    if self.LOCAL_DATABASE and self.LOCAL_DATABASE_URL:
        return self.LOCAL_DATABASE_URL
    
    return self.DATABASE_URL
```

### Приоритет:
1. **TESTING=true** → использует `TEST_DATABASE_URL` и `TEST_REDIS_URL`
2. **LOCAL_DATABASE=true** → использует `LOCAL_DATABASE_URL` и `LOCAL_REDIS_URL`
3. **По умолчанию** → использует `DATABASE_URL` и `REDIS_URL` (Docker)

---

## 🎯 Рекомендации

### Для разработки:
- Используйте **локальный запуск** для быстрой итерации
- БД и Redis через Docker, API локально
- Hot reload работает быстрее

### Для тестирования:
- Можно запускать **локально** или **в Docker**
- Локально быстрее, в Docker ближе к production

### Для production:
- Только **Docker** с `LOCAL_DATABASE=false`
- Все сервисы в контейнерах

---

# API документация

## Moderator Panel (`/api/v1/moderator`)

Панель модерации контента. Доступна для ролей: `moderator`, `official`, `admin`.

### Комментарии с жалобами

#### `GET /moderator/comments/flagged`
Получить список комментариев с жалобами от пользователей.

**Query параметры:**
- `offset` (int, default=0) — смещение для пагинации
- `limit` (int, default=20, max=100) — количество записей

**Response:**
```json
{
  "items": [
    {
      "entity_id": 123,
      "problem_entity_id": 456,
      "author_entity_id": 789,
      "content": "Текст комментария",
      "is_flagged": true,
      "flag_reason": "Спам",
      "created_at": "2026-04-07T10:00:00"
    }
  ],
  "total": 10,
  "offset": 0,
  "limit": 20
}
```

#### `POST /moderator/comments/{entity_id}/hide`
Скрыть комментарий нарушающий правила.

**Body:**
```json
{
  "reason": "Нарушение правил сообщества"
}
```

#### `POST /moderator/comments/{entity_id}/restore`
Восстановить скрытый комментарий.

---

### Подозрительные проблемы

#### `GET /moderator/problems/suspicious`
Проблемы с низким truth_score — возможные фейки.

**Query параметры:**
- `threshold` (float, default=0.3) — порог truth_score (0.0-1.0)
- `offset` (int, default=0)
- `limit` (int, default=20, max=100)

#### `GET /moderator/problems/pending`
Новые проблемы требующие проверки.

#### `POST /moderator/problems/{entity_id}/verify`
Подтвердить проблему как валидную.

---

### Статистика модератора

#### `GET /moderator/stats`
Статистика работы текущего модератора.

**Response:**
```json
{
  "problems_verified": 45,
  "problems_rejected": 12,
  "comments_hidden": 8,
  "users_suspended": 3,
  "flagged_pending": 5,
  "suspicious_pending": 2
}
```

---

## Official Panel (`/api/v1/official`)

Панель для официальных лиц и городских служб. Доступна для ролей: `official`, `admin`.

### Управление проблемами

#### `GET /official/problems/assigned`
Проблемы назначенные на текущего официала.

**Query параметры:**
- `status` (ProblemStatus, optional) — фильтр по статусу
- `offset` (int, default=0)
- `limit` (int, default=20, max=100)

#### `GET /official/problems/in-progress`
Проблемы в работе у текущего официала.

#### `POST /official/problems/{entity_id}/take`
Взять проблему в работу.

**Body:**
```json
{
  "note": "Взято в работу городской службой"
}
```

#### `POST /official/problems/{entity_id}/resolve`
Отметить проблему решённой с отчётом.

**Body:**
```json
{
  "resolution_note": "Яма заделана, дорога отремонтирована",
  "actual_work_done": "Асфальтирование 10м²"
}
```

#### `POST /official/problems/{entity_id}/comment`
Добавить официальный ответ от городских служб.

**Body:**
```json
{
  "content": "Работы запланированы на следующую неделю",
  "estimated_resolution_date": "2026-04-15T10:00:00"
}
```

---

### Зоны

#### `GET /official/zones`
Зоны закреплённые за официалом (зоны города официала).

---

### Статистика официала

#### `GET /official/stats`
Статистика работы текущего официала.

**Response:**
```json
{
  "problems_assigned": 45,
  "problems_in_progress": 8,
  "problems_resolved": 37,
  "avg_resolution_days": 3.5,
  "zones_managed": 4,
  "official_responses": 52
}
```

---

## Права доступа

| Действие | user | volunteer | moderator | official | admin |
|----------|------|-----------|-----------|----------|-------|
| Просмотр жалоб на комментарии | ❌ | ❌ | ✅ | ✅ | ✅ |
| Скрытие комментариев | ❌ | ❌ | ✅ | ✅ | ✅ |
| Просмотр подозрительных проблем | ❌ | ❌ | ✅ | ✅ | ✅ |
| Подтверждение проблем | ❌ | ❌ | ✅ | ✅ | ✅ |
| Взятие проблемы в работу | ❌ | ❌ | ❌ | ✅ | ✅ |
| Решение проблемы | ❌ | ✅ | ✅ | ✅ | ✅ |
| Официальный ответ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Просмотр зон | ❌ | ❌ | ❌ | ✅ | ✅ |

---

# Roadmap развития

## 📊 Текущее состояние проекта

### Реализовано ✅
- Базовая система проблем с геолокацией
- Система голосования с весами репутации
- Комментарии с вложенностью
- Зоны с иерархией и статистикой
- Медиа (фото/видео) с EXIF
- Симуляции событий
- Панели модератора и официальных лиц
- Версионирование всех изменений
- Celery задачи для фоновой обработки
- JWT аутентификация
- Система ролей (user/volunteer/moderator/official/admin)

### Архитектура
- FastAPI + PostgreSQL/PostGIS + Redis + Celery
- Event Sourcing (версионирование)
- RESTful API
- Docker + docker-compose
- Alembic миграции
- Pytest тесты

---

## 🚀 Приоритетные фичи (MVP+)

### 1. Уведомления и подписки 🔔
**Зачем:** Пользователи должны знать об изменениях в проблемах

**Что добавить:**
- Email уведомления (уже есть SMTP)
- Push уведомления (WebPush)
- Подписки на проблемы
- Подписки на зоны (район)
- Настройки уведомлений пользователя
- Дайджест (еженедельная сводка)

---

### 2. Расширенная аналитика и дашборды 📈
**Зачем:** Власти и граждане должны видеть динамику

**Что добавить:**
- Временные графики (проблемы по дням/неделям/месяцам)
- Сравнение районов
- Топ проблемных зон
- Рейтинг активных пользователей
- Эффективность официалов (время решения)
- Прогнозы (ML) — какие зоны станут проблемными
- Экспорт данных (CSV, Excel, PDF)
- Публичные дашборды для СМИ

---

### 3. Интеграции с внешними системами 🔗
**Зачем:** Автоматизация и расширение функциональности

**Что добавить:**
- Telegram бот
- WhatsApp бот
- Интеграция с городскими службами
- Интеграция с картами (Google Maps, OpenStreetMap, 2GIS)
- Интеграция с погодой
- Интеграция с транспортом

---

### 4. Геймификация и репутация 🎮
**Зачем:** Мотивация пользователей быть активными

**Что добавить:**
- Достижения (badges)
- Уровни пользователей
- Рейтинги
- Награды и бонусы
- Челленджи (месячные задания)

---

### 5. AI и ML функции 🤖
**Зачем:** Автоматизация модерации и улучшение качества

**Что добавить:**
- Автоматическая категоризация проблем (ML)
- Определение дубликатов проблем
- Анализ тональности комментариев
- Распознавание объектов на фото (CV)
- Автоматическое определение координат по фото
- Предсказание времени решения
- Рекомендации похожих проблем
- Автоматическая модерация (спам, токсичность)

---

### 6. Мобильное приложение 📱
**Зачем:** Большинство пользователей на мобильных

**Что нужно:**
- React Native / Flutter приложение
- Камера для фото проблем
- Геолокация автоматически
- Push уведомления
- Офлайн режим (синхронизация)
- Карта с проблемами
- QR коды для быстрого доступа

---

### 7. Социальные функции 👥
**Зачем:** Вовлечение сообщества

**Что добавить:**
- Профили пользователей
- Подписки на пользователей
- Лента активности
- Упоминания (@username)
- Хештеги (#яма #дорога)
- Шаринг в соцсети
- Группы/сообщества по районам
- Петиции (сбор подписей)

---

### 8. Расширенная модерация 🛡️
**Зачем:** Качество контента

**Что добавить:**
- Очередь модерации с приоритетами
- Автоматические правила модерации
- Блокировка пользователей
- История модерации
- Апелляции на решения модераторов
- Система репортов (жалобы)
- Whitelist/Blacklist слов
- Карантин для новых пользователей

---

### 9. Финансирование и краудфандинг 💰
**Зачем:** Решение проблем требует денег

**Что добавить:**
- Краудфандинг для проблем
- Интеграция с платёжными системами
- Прозрачность расходов
- Отчёты о потраченных средствах
- Спонсорство от бизнеса
- Гранты от властей

---

### 10. API для разработчиков 🔧
**Зачем:** Экосистема приложений

**Что добавить:**
- Public API с ключами
- Rate limiting
- API документация (OpenAPI)
- Webhooks
- GraphQL API (опционально)
- SDK для популярных языков
- Песочница для тестирования

---

## 🏗️ Технические улучшения

### Производительность
- Кеширование (Redis)
- CDN для медиа
- Оптимизация запросов (N+1)
- Индексы БД
- Пагинация cursor-based
- Lazy loading для больших списков

### Безопасность
- Rate limiting (защита от DDoS)
- CAPTCHA для регистрации
- 2FA (двухфакторная аутентификация)
- Аудит безопасности
- HTTPS обязательно
- CSP заголовки
- Защита от SQL injection (уже есть через ORM)
- XSS защита

### Мониторинг
- Sentry для ошибок
- Prometheus + Grafana для метрик
- Логирование (ELK stack)
- Health checks
- Алерты при проблемах

### CI/CD
- GitHub Actions / GitLab CI
- Автоматические тесты
- Автоматический деплой
- Staging окружение
- Blue-green deployment

---

## 📅 Предлагаемый план развития

### Фаза 1 (1-2 месяца) — Базовые улучшения
1. ✅ Панели модератора и официальных лиц (ГОТОВО)
2. Уведомления (email + in-app)
3. Подписки на проблемы
4. Расширенная аналитика
5. Telegram бот (базовый)

### Фаза 2 (2-3 месяца) — Социальные функции
1. Профили пользователей
2. Геймификация (достижения, уровни)
3. Лента активности
4. Мобильное приложение (MVP)
5. Push уведомления

### Фаза 3 (3-4 месяца) — AI и автоматизация
1. ML категоризация проблем
2. Определение дубликатов
3. Распознавание объектов на фото
4. Автоматическая модерация
5. Предсказание времени решения

### Фаза 4 (4-6 месяцев) — Интеграции и масштабирование
1. Интеграция с городскими службами
2. API для разработчиков
3. Краудфандинг
4. Производительность и кеширование
5. Мониторинг и алерты

---

## 🎯 Метрики успеха

### Пользовательские
- Количество активных пользователей (DAU/MAU)
- Количество созданных проблем
- Процент решённых проблем
- Среднее время решения
- Вовлечённость (комментарии, голоса)

### Технические
- Uptime > 99.9%
- Response time < 200ms (p95)
- Test coverage > 80%
- Zero critical bugs

### Бизнес
- Количество городов
- Количество официальных партнёров
- Медиа упоминания
- Социальный эффект (решённые проблемы)

---

**Проект имеет огромный потенциал для развития! 🚀**