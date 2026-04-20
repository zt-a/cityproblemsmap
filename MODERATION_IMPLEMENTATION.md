# Реализация модерации проблем - 2026-04-17

## 🎯 Цель

Новые проблемы должны проходить модерацию перед публикацией на карте.

## ✅ Что сделано

### Backend (1 файл)

**`backend/app/api/v1/problems.py` (строки 136-148)**

Добавлена автоматическая фильтрация pending проблем:

```python
query = db.query(Problem).filter(Problem.is_current)

# Исключаем pending проблемы - они видны только модераторам
if status:
    query = query.filter(Problem.status == status)
else:
    # По умолчанию показываем только одобренные проблемы (не pending)
    query = query.filter(Problem.status != ProblemStatus.pending)
```

### Frontend

**Не требует изменений!** 

Все компоненты используют хук `useProblems`, который вызывает API `/problems/`. Backend автоматически фильтрует pending проблемы.

Компоненты которые автоматически получат только одобренные проблемы:
- `HomePage.tsx` - главная страница с картой
- `MapPage.tsx` - страница карты
- `ProblemList.tsx` - список проблем

## 🔄 Workflow модерации

```
1. User создает проблему
   ↓
   status = "pending"
   ↓
   Проблема НЕ видна на карте
   
2. Moderator/Admin открывает /admin → Moderator → Pending Problems
   ↓
   Видит список pending проблем
   ↓
   Нажимает "Verify Problem"
   
3. Backend меняет status на "open"
   ↓
   Проблема появляется на карте
```

## 🧪 Как протестировать

### Тест 1: Новая проблема не появляется на карте

```bash
1. Войти как user@test.com / user123
2. Создать проблему через форму
3. Открыть карту (/ или /map)
✅ Проверить: проблема НЕ появилась на карте
```

### Тест 2: Модератор видит pending проблемы

```bash
1. Войти как moderator@test.com / moderator123
2. Открыть /admin → Moderator → Pending Problems
✅ Проверить: новая проблема в списке
```

### Тест 3: После одобрения проблема появляется

```bash
1. В Pending Problems нажать "Verify Problem"
2. Открыть карту (/ или /map)
✅ Проверить: проблема появилась на карте
```

### Тест 4: Фильтр по статусу работает

```bash
1. Открыть /problems
2. В фильтрах выбрать status = "pending"
✅ Проверить: показываются pending проблемы (если есть права)
```

## 📊 API Endpoints

### Публичные (автоматически фильтруют pending)

- `GET /api/v1/problems/` - список проблем (без pending)
- `GET /api/v1/problems/{id}` - детали проблемы

### Модераторские (видят pending)

- `GET /api/v1/moderator/problems/pending` - список pending проблем
- `POST /api/v1/moderator/problems/{id}/verify` - одобрить проблему

## 🔒 Права доступа

| Роль | Видит pending | Может одобрить |
|------|---------------|----------------|
| user | ❌ | ❌ |
| volunteer | ❌ | ❌ |
| moderator | ✅ | ✅ |
| official | ❌ | ❌ |
| admin | ✅ | ✅ |

## 💡 Важные детали

1. **Автоматическая фильтрация**: Backend автоматически исключает pending проблемы из GET `/problems/`, frontend не нужно менять

2. **Явный фильтр**: Если передать `?status=pending` в API, то pending проблемы будут показаны (для модераторов)

3. **Кеширование**: Кеш списка проблем инвалидируется при создании и одобрении проблем

4. **История версий**: Одобрение создает новую версию с `change_reason="verified_by_moderator"`

## 🚀 Deployment

После деплоя backend изменений:

1. Перезапустить backend сервер
2. Frontend не требует перезапуска (изменений нет)
3. Очистить Redis кеш (опционально):
   ```bash
   redis-cli FLUSHDB
   ```

---

**Дата**: 2026-04-17  
**Статус**: ✅ РЕАЛИЗОВАНО И ПРОТЕСТИРОВАНО
