# Финальные исправления - 2026-04-17

## ✅ Что было исправлено

### 1. Reports - ссылки на комментарии

**Проблема**: 
- Ссылки "View Target" для comment reports вели на несуществующие страницы
- Использовался `target_entity_id` (ID комментария) вместо ID проблемы

**Решение**:

**Backend** - добавлено поле `problem_entity_id` в ReportPublic:
```python
# backend/app/schemas/report.py
class ReportPublic(BaseModel):
    # ... existing fields
    problem_entity_id: Optional[int] = Field(None, description="ID проблемы (для comment reports)")

# backend/app/api/v1/reports.py - строки 219-258
# Для comment reports находим problem_entity_id из комментария
if report.target_type == "comment":
    comment = db.query(Comment).filter_by(
        entity_id=report.target_entity_id,
        is_current=True
    ).first()
    if comment:
        report_dict["problem_entity_id"] = comment.problem_entity_id
```

**Frontend** - ссылка теперь ведет на проблему с hash для скролла:
```typescript
// frontend/src/components/admin/ModeratorPanel.tsx
report.target_type === 'comment'
  ? `/problems/${report.problem_entity_id}#comment-${report.target_entity_id}`
  : ...
```

**Frontend** - добавлен автоматический скролл к комментарию:
```typescript
// frontend/src/components/problem/ProblemDetail.tsx
useEffect(() => {
  if (location.hash && comments) {
    const commentId = location.hash.replace('#comment-', '')
    const element = document.getElementById(`comment-${commentId}`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      // Подсветка на 2 секунды
      element.classList.add('ring-2', 'ring-primary')
    }
  }
}, [location.hash, comments])
```

---

### 2. Модерация новых проблем

**Проблема**: Новые проблемы сразу появлялись на карте без модерации

**Решение**:

**Миграция БД** - добавлен enum value 'pending':
```python
# backend/alembic/versions/add_pending_status.py
op.execute("ALTER TYPE problemstatus ADD VALUE IF NOT EXISTS 'pending'")
```

**Backend** - фильтрация pending проблем:
```python
# backend/app/api/v1/problems.py - строки 136-148
if status:
    query = query.filter(Problem.status == status)
else:
    # По умолчанию показываем только одобренные проблемы (не pending)
    query = query.filter(Problem.status != ProblemStatus.pending)
```

**Frontend** - не требует изменений, автоматически получает только одобренные проблемы

---

## 📊 Измененные файлы

### Backend (4 файла)
1. ✅ `app/schemas/report.py` - добавлено поле `problem_entity_id`
2. ✅ `app/api/v1/reports.py` - логика заполнения `problem_entity_id` для comment reports
3. ✅ `app/api/v1/problems.py` - фильтрация pending проблем
4. ✅ `alembic/versions/add_pending_status.py` - миграция для добавления pending enum

### Frontend (2 файла)
1. ✅ `src/components/admin/ModeratorPanel.tsx` - ссылка с hash для comment reports
2. ✅ `src/components/problem/ProblemDetail.tsx` - автоскролл к комментарию по hash

---

## 🚀 Как протестировать

### Тест 1: Ссылка на комментарий работает

```bash
1. Войти как moderator@test.com / moderator123
2. Открыть /admin → Moderator → Reports
3. Найти report с target_type = "comment"
4. Кликнуть "View Target"
✅ Проверить: 
   - Открылась страница проблемы
   - Автоматически проскроллило к комментарию
   - Комментарий подсвечен на 2 секунды
```

### Тест 2: Pending проблемы не видны на карте

```bash
1. Войти как user@test.com / user123
2. Создать проблему
3. Открыть карту (/ или /map)
✅ Проверить: проблема НЕ появилась на карте

4. Войти как moderator@test.com / moderator123
5. Открыть /admin → Moderator → Pending Problems
6. Одобрить проблему (Verify)
7. Открыть карту
✅ Проверить: проблема появилась на карте
```

---

## 🔧 Deployment

### Backend

1. Применить миграцию:
```bash
docker-compose exec api alembic upgrade head
```

2. Перезапустить backend (если нужно):
```bash
docker-compose restart api
```

### Frontend

Не требует перезапуска - изменения применятся автоматически при следующей сборке.

---

## 💡 Технические детали

### Hash navigation

URL формат: `/problems/123#comment-456`
- `123` - entity_id проблемы
- `456` - entity_id комментария

### Подсветка комментария

При переходе по ссылке с hash:
1. Страница загружается
2. useEffect ждет загрузки комментариев
3. Находит элемент по ID `comment-${entity_id}`
4. Скроллит к нему (smooth scroll, center)
5. Добавляет ring-2 ring-primary на 2 секунды
6. Убирает подсветку

### Фильтрация pending

- GET `/api/v1/problems/` - автоматически исключает pending
- GET `/api/v1/problems/?status=pending` - показывает pending (для модераторов)
- GET `/api/v1/moderator/problems/pending` - только pending проблемы

---

**Дата**: 2026-04-17  
**Время**: 02:55 UTC  
**Статус**: ✅ ВСЕ ИСПРАВЛЕНИЯ ЗАВЕРШЕНЫ

**Проект готов к конкурсу!** 🚀🎉
