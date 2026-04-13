# Reports System - Система жалоб

Полная реализация системы жалоб для CityProblemMap.

## Компоненты

### 1. ReportModal
Модальное окно для создания жалобы на проблему, комментарий или пользователя.

**Использование:**
```tsx
import { ReportModal } from '../components/ReportModal';

const [isReportModalOpen, setIsReportModalOpen] = useState(false);

<ReportModal
  isOpen={isReportModalOpen}
  onClose={() => setIsReportModalOpen(false)}
  targetType="problem" // "problem" | "comment" | "user"
  targetEntityId={123}
  targetTitle="Название проблемы" // опционально
/>
```

**Props:**
- `isOpen` - состояние открытия модалки
- `onClose` - callback для закрытия
- `targetType` - тип объекта жалобы (problem/comment/user)
- `targetEntityId` - ID объекта
- `targetTitle` - название объекта (опционально, для отображения)

**Причины жалоб:**
- `spam` - Спам
- `offensive` - Оскорбительный контент
- `inappropriate` - Неуместный контент
- `false_info` - Ложная информация
- `duplicate` - Дубликат
- `other` - Другое

### 2. MyReports
Страница для просмотра своих жалоб.

**Роут:** `/reports`

**Функционал:**
- Список всех жалоб пользователя
- Фильтрация по статусу (все/на рассмотрении/одобрено/отклонено)
- Отображение ответов модераторов
- Статистика жалоб

## API Endpoints

### Создать жалобу
```typescript
POST /api/v1/reports/
Body: {
  target_type: "problem" | "comment" | "user",
  target_entity_id: number,
  reason: string,
  description?: string | null
}
```

### Получить свои жалобы
```typescript
GET /api/v1/reports/my
Query: {
  status_filter?: string,
  offset?: number,
  limit?: number
}
```

### Очередь модерации (только для модераторов)
```typescript
GET /api/v1/reports/moderation/queue
Query: {
  status_filter?: string,
  target_type?: string,
  offset?: number,
  limit?: number
}
```

### Разрешить жалобу (только для модераторов)
```typescript
PATCH /api/v1/reports/moderation/{entity_id}/resolve
Body: {
  action: "approve" | "reject",
  resolution_note?: string
}
```

### Статистика жалоб (только для модераторов)
```typescript
GET /api/v1/reports/moderation/stats
```

## Интеграция

### В ProblemDetail
Кнопка "Пожаловаться" уже интегрирована в `ProblemDetail.tsx`:
```tsx
<button onClick={() => setIsReportModalOpen(true)}>
  <Flag className="w-4 h-4" />
  <span>Пожаловаться</span>
</button>
```

### В комментариях
Добавьте аналогичную кнопку в компонент комментария:
```tsx
<button onClick={() => setIsReportModalOpen(true)}>
  <Flag className="w-3 h-3" />
  Пожаловаться
</button>

<ReportModal
  isOpen={isReportModalOpen}
  onClose={() => setIsReportModalOpen(false)}
  targetType="comment"
  targetEntityId={comment.entity_id}
/>
```

### В профиле пользователя
```tsx
<ReportModal
  isOpen={isReportModalOpen}
  onClose={() => setIsReportModalOpen(false)}
  targetType="user"
  targetEntityId={user.entity_id}
  targetTitle={user.username}
/>
```

## Навигация

Страница "Мои жалобы" добавлена в Sidebar:
- Desktop: боковая панель, иконка Flag
- Mobile: нижняя навигация

## Статусы жалоб

- `pending` - На рассмотрении (желтый)
- `approved` - Одобрено (зеленый)
- `rejected` - Отклонено (красный)

## Дизайн

Все компоненты следуют dark theme дизайну приложения:
- Background: `#111827`, `#1F2937`
- Accent: `#F59E0B` (оранжевый для жалоб)
- Text: `#E5E7EB`, `#9CA3AF`
- Borders: `#374151`

## Безопасность

- Ложные жалобы могут привести к снижению репутации пользователя
- Модераторы получают уведомления о новых жалобах
- История всех жалоб сохраняется для аудита
