# Frontend исправления - 2026-04-17

## ✅ Исправлено

### 1. NotificationBell.tsx
- ✅ `notification.problem_id` → `notification.problem_entity_id`
- ✅ `notification.actor_id` → `notification.actor_entity_id`

### 2. NotificationsPage.tsx
- ✅ `notification.problem_id` → `notification.problem_entity_id`
- ✅ `notification.actor_id` → `notification.actor_entity_id`

## 📝 Что нужно сделать

### Регенерация API клиента

После запуска backend нужно регенерировать API клиент:

```bash
cd frontend
npm run generate-api
```

Это обновит типы в `src/api/generated/` с правильными полями:
- `problem_entity_id` вместо `problem_id`
- `comment_entity_id` вместо `comment_id`
- `actor_entity_id` вместо `actor_id`

### Проверка после регенерации

1. Проверить что TypeScript не выдает ошибок:
```bash
npm run type-check
```

2. Запустить dev сервер:
```bash
npm run dev
```

3. Протестировать уведомления:
   - Создать проблему
   - Добавить комментарий от другого пользователя
   - Проверить колокольчик уведомлений
   - Открыть /notifications

## 🎯 Статус

✅ **Frontend код исправлен**
⚠️ **Требуется регенерация API клиента** (после запуска backend)

---

**Дата**: 2026-04-17
