# CityProblemMap — Статус проекта и нереализованные фичи

> Дата обновления: 2026-04-14  
> Для быстрого старта после перезапуска Claude

---

## 📋 О проекте

**CityProblemMap** — civic tech платформа для сообщения о городских проблемах с геолокацией, голосованием и прозрачным решением.

### Технологический стек

**Backend:**
- FastAPI + PostgreSQL/PostGIS + Redis + Celery
- Event Sourcing (append-only с версионированием)
- JWT аутентификация
- Система ролей: user, volunteer, moderator, official, admin

**Frontend:**
- React + TypeScript + Vite
- TanStack Query (React Query)
- React Router
- Tailwind CSS
- React Leaflet (карты)
- OpenAPI code generation

---

## ✅ Реализовано в Frontend

### Основные фичи
- ✅ Аутентификация (JWT с автоматическим refresh)
- ✅ Карта с проблемами (React Leaflet, 4 темы карт)
- ✅ Создание проблем с геолокацией и медиа
- ✅ Детальная страница проблемы (ProblemDetail)
- ✅ Комментарии с вложенностью (replies)
- ✅ Голосование (правда/фейк + urgency/impact/inconvenience)
- ✅ Медиа галерея (фото/видео)
- ✅ История изменений (timeline)
- ✅ Карточки проблем с автоматической сменой фото (3 сек + ручное управление)
- ✅ Координаты и навигация (2GIS)
- ✅ Мобильная адаптация
- ✅ Редактирование проблем (для автора) с управлением медиа
- ✅ Публичные профили пользователей
- ✅ Система подписок (follow/unfollow)
- ✅ Лента активности (activity feed)
- ✅ Кликабельные имена пользователей по всему приложению

### Социальные функции
- ✅ UserProfilePage — публичные профили с аватаром, био, статистикой
- ✅ Кнопка Follow/Unfollow с проверкой статуса подписки
- ✅ Счетчики подписчиков/подписок
- ✅ Список проблем пользователя на его странице
- ✅ Activity Feed — лента действий от подписок
- ✅ UserName компонент с аватарами и ссылками на профили
- ✅ Навигация к ленте через Sidebar (/feed)

### Система оценок
- ✅ Truth Score (достоверность 0-100%)
- ✅ Priority Score (приоритет 0.0-1.0)
- ✅ Взвешенное голосование по репутации
- ✅ Автоматический пересчёт scores
- ✅ Документация в `SCORING_SYSTEM.md`

### Технические детали
- ✅ Автоматический refresh JWT токенов (axios interceptors)
- ✅ OpenAPI code generation с post-generation патчингом
- ✅ Event Sourcing на фронте (версионирование голосов)
- ✅ Ограничение изменения голоса (1 раз)
- ✅ URL параметры для deep linking (/map?lat=...&lng=...)
- ✅ localStorage для настроек (тема карты)
- ✅ Медиа менеджмент (загрузка/удаление) в форме редактирования

---

## ❌ НЕ реализовано в Frontend

### 1. Прозрачность данных (детальная история версий) 📜
**Приоритет: СРЕДНИЙ**

**Что есть в бэкенде:**
- Event Sourcing — все изменения сохраняются
- Каждая версия имеет: version, changed_by_id, change_reason, created_at

**Что уже реализовано:**
- ✅ Timeline с историей изменений в ProblemDetail
- ✅ Показываются версии, статусы, scores

**Что можно улучшить:**
- Diff между версиями (показать что именно изменилось)
- Кто именно внес изменение (changed_by_id → username)
- Фильтрация истории (только статусы, только scores, и т.д.)

---

### 2. Панели для модераторов/официальных лиц 👮
**Приоритет: ВЫСОКИЙ**

**Что нужно сделать:**
- `src/components/problem/ProblemHistory.tsx` — детальная история
- API endpoint для получения всех версий проблемы
- Визуализация изменений (было → стало)

---

### 5. Админ панели (moderator/official/volunteer) 🛡️
**Приоритет: СРЕДНИЙ**

**API готово:**
- `/api/v1/moderator/*` — панель модератора
- `/api/v1/official/*` — панель официальных лиц
- `/api/v1/admin/*` — админ панель

**Moderator Panel:**
- `GET /moderator/comments/flagged` — комментарии с жалобами
- `POST /moderator/comments/{id}/hide` — скрыть комментарий
- `GET /moderator/problems/suspicious` — подозрительные проблемы
- `GET /moderator/problems/pending` — новые проблемы
- `POST /moderator/problems/{id}/verify` — подтвердить проблему
- `GET /moderator/stats` — статистика модератора

**Official Panel:**
- `GET /official/problems/assigned` — назначенные проблемы
- `POST /official/problems/{id}/take` — взять в работу
- `POST /official/problems/{id}/resolve` — решить проблему
- `POST /official/problems/{id}/comment` — официальный ответ
- `GET /official/zones` — зоны официала
- `GET /official/stats` — статистика

**Что нужно сделать:**
- `src/pages/ModeratorDashboard.tsx`
- `src/pages/OfficialDashboard.tsx`
- `src/components/moderator/*` — компоненты модерации
- `src/components/official/*` — компоненты для официалов
- Роуты `/moderator`, `/official`
- Проверка ролей (role-based access)

---

### 6. Спец ответы в комментариях 💬
**Приоритет: СРЕДНИЙ**

**Что нужно:**
- Бейджи для официальных лиц (official, moderator, admin)
- Выделение официальных ответов (другой цвет, иконка)
- Закрепление важных комментариев (pinned)

**API:**
- Уже есть `user.role` в комментариях
- `POST /official/problems/{id}/comment` — создаёт официальный комментарий

**Что нужно сделать:**
- Обновить `CommentItem.tsx` — показывать бейджи ролей
- Стили для официальных комментариев
- Фильтр "Только официальные ответы"

---

### 7. Зоны (zones) 🗺️
**Приоритет: НИЗКИЙ**

**API готово:**
- `GET /api/v1/zones` — список зон
- `GET /api/v1/zones/{id}` — детали зоны
- `GET /api/v1/zones/{id}/problems` — проблемы в зоне
- `GET /api/v1/zones/{id}/stats` — статистика зоны

**Что такое зоны:**
- Административные районы города (иерархия)
- Каждая зона имеет: name, parent_zone_id, geometry (polygon)
- Проблемы привязаны к зонам по координатам

**Что нужно сделать:**
- Визуализация зон на карте (полигоны)
- Фильтр проблем по зоне
- Страница зоны с статистикой
- Сравнение зон (аналитика)

**Вопросы:**
- Как показывать иерархию зон?
- Нужен ли выбор зоны при создании проблемы?
- Как визуализировать границы зон на карте?

---

### 8. Аналитика 📊
**Приоритет: СРЕДНИЙ**

**API готово:**
- `GET /api/v1/analytics` — базовая статистика
- `GET /api/v1/analytics/extended` — расширенная аналитика

**Что показывать:**
- Графики по времени (проблемы по дням/неделям)
- Распределение по категориям
- Топ проблем по приоритету
- Карта тепла (heatmap) проблем
- Статистика решений (среднее время)
- Сравнение зон

**Что нужно сделать:**
- `src/pages/AnalyticsPage.tsx`
- Библиотека графиков (recharts или chart.js)
- `src/components/analytics/ProblemChart.tsx`
- `src/components/analytics/HeatMap.tsx`
- Фильтры по датам, категориям, зонам

---

### 9. Fundraising (краудфандинг) 💰
**Приоритет: НИЗКИЙ**

**API готово:**
- `POST /api/v1/fundraising/campaigns` — создать кампанию
- `GET /api/v1/fundraising/campaigns/{id}` — детали кампании
- `POST /api/v1/fundraising/campaigns/{id}/donate` — пожертвовать

**Что нужно:**
- Страница кампании с прогресс-баром
- Интеграция с платёжными системами
- Прозрачность расходов
- История пожертвований

---

### 10. Уведомления 🔔
**Приоритет: СРЕДНИЙ**

**API готово:**
- `GET /api/v1/notifications` — список уведомлений
- `PATCH /api/v1/notifications/{id}/read` — отметить прочитанным
- `GET /api/v1/subscriptions` — подписки на проблемы

**Что нужно:**
- Иконка колокольчика с счётчиком
- Dropdown с уведомлениями
- Страница всех уведомлений
- Настройки уведомлений
- WebSocket для real-time (опционально)

---

## 🎯 Рекомендуемый порядок реализации

### Фаза 1: User Experience (1-2 недели)
1. **Редактирование проблем** — быстро, улучшит UX
2. **Публичные профили** — база для social
3. **Social функционал** — подписки, лента

### Фаза 2: Community (1-2 недели)
4. **Спец ответы** — бейджи для официалов
5. **Уведомления** — вовлечение пользователей
6. **Прозрачность данных** — показать историю

### Фаза 3: Governance (2-3 недели)
7. **Moderator Panel** — модерация контента
8. **Official Panel** — работа с проблемами
9. **Аналитика** — дашборды и графики

### Фаза 4: Advanced (опционально)
10. **Зоны** — визуализация районов
11. **Fundraising** — краудфандинг

---

## 📝 Важные файлы для контекста

### Backend документация
- `/backend/PROJECT_DOCUMENTATION.md` — полная документация API
- `/backend/CLAUDE.md` — инструкции для Claude
- `SCORING_SYSTEM.md` — система оценок

### Frontend структура
```
src/
├── api/generated/          # Сгенерированный API клиент
├── components/
│   ├── problem/           # Компоненты проблем
│   ├── map/               # Карта
│   ├── layout/            # Layout (Header, Sidebar)
│   └── auth/              # Аутентификация
├── hooks/                 # React hooks
│   ├── useAuth.ts
│   ├── useProblems.ts
│   ├── useVotes.ts
│   ├── useComments.ts
│   └── useMedia.ts
├── pages/                 # Страницы
│   ├── MapPage.tsx
│   ├── ProblemDetailPage.tsx
│   └── ...
└── utils/                 # Утилиты
```

---

## 🔧 Технические детали

### Event Sourcing
- Все изменения append-only
- Каждая версия имеет: entity_id, version, is_current
- `is_current=true` — актуальная версия
- История доступна через `version` и `superseded_at`

### Система ролей
```python
class UserRole(str, Enum):
    user = "user"           # Обычный пользователь
    volunteer = "volunteer" # Волонтёр (может решать проблемы)
    moderator = "moderator" # Модератор (модерация контента)
    official = "official"   # Официальное лицо (городские службы)
    admin = "admin"         # Администратор (полный доступ)
```

### Scoring System
- **Truth Score** = weighted_votes("правда") / total_weighted_votes
- **Priority Score** = truth×0.35 + urgency×0.30 + impact×0.25 + inconvenience×0.10
- Веса голосов по репутации: 1.0 (новичок) → 2.5 (эксперт)

---

## 💡 Команда для быстрого старта

```bash
# После перезапуска Claude скажи:
"загрузи память и прочитай PROJECT_STATUS.md"

# Затем выбери задачу:
"давай реализуем редактирование проблем"
"давай сделаем публичные профили"
"давай добавим social функционал"
```

---

**Последнее обновление:** 2026-04-14  
**Статус:** Frontend базовый функционал готов, нужны social/admin фичи
