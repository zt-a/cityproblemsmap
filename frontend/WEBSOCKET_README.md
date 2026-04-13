# WebSocket Real-Time Notifications

Интеграция WebSocket для получения уведомлений в реальном времени.

## 🔌 Архитектура

### Backend
- **Endpoint:** `ws://localhost:8000/api/v1/ws/notifications?token=JWT_TOKEN`
- **Технология:** FastAPI WebSocket + Redis Pub/Sub
- **Аутентификация:** JWT токен в query параметре

### Frontend
- **Хук:** `useWebSocketNotifications`
- **Автоматическое переподключение:** Да (каждые 5 секунд)
- **Интеграция:** Header + Notifications страница

## 📡 Типы событий

WebSocket отправляет следующие типы уведомлений:

```typescript
{
  type: "new_comment" | "status_changed" | "new_vote" | 
        "official_response" | "problem_solved" | "new_follower",
  message: string,
  notification_id?: number,
  problem_id?: number,
  comment_id?: number,
  user_id?: number,
  created_at?: string
}
```

### Типы событий:
- `new_comment` - Новый комментарий на проблеме
- `status_changed` - Статус проблемы изменился
- `new_vote` - Новый голос
- `official_response` - Официальный ответ
- `problem_solved` - Проблема решена
- `new_follower` - Новый подписчик

## 🎯 Использование

### 1. Хук useWebSocketNotifications

```typescript
import { useWebSocketNotifications } from '../hooks/useWebSocketNotifications';

const MyComponent = () => {
  useWebSocketNotifications({
    onMessage: (data) => {
      console.log('New notification:', data);
      // Обработка уведомления
    },
    onConnect: () => {
      console.log('WebSocket connected');
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected');
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    },
    autoReconnect: true,
    reconnectInterval: 5000,
  });
};
```

### 2. Интеграция в Header

```typescript
// Header автоматически:
// 1. Подключается к WebSocket при авторизации
// 2. Обновляет список уведомлений при получении новых
// 3. Показывает browser notification (если разрешено)
// 4. Обновляет счетчик непрочитанных
```

### 3. Интеграция в Notifications страницу

```typescript
// Страница Notifications автоматически:
// 1. Подключается к WebSocket
// 2. Обновляет список при получении новых уведомлений
// 3. Обновляет статистику
```

## 🔧 Конфигурация

### Environment Variables

```env
# .env
VITE_WS_BASE_URL=ws://localhost:8000/api/v1/ws
```

### WebSocket URL

```typescript
const wsUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/api/v1/ws';
const ws = new WebSocket(`${wsUrl}/notifications?token=${token}`);
```

## 🔐 Аутентификация

WebSocket использует JWT токен из localStorage:

```typescript
const token = getStoredToken(); // из localStorage
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/notifications?token=${token}`);
```

## 🔄 Автоматическое переподключение

Хук автоматически переподключается при разрыве соединения:

```typescript
{
  autoReconnect: true,        // Включить автопереподключение
  reconnectInterval: 5000,    // Интервал в миллисекундах
}
```

## 🔔 Browser Notifications

Header автоматически показывает browser notifications при получении новых уведомлений:

```typescript
if ('Notification' in window && Notification.permission === 'granted') {
  new Notification('CityProblemMap', {
    body: data.message,
    icon: '/favicon.ico',
  });
}
```

### Запрос разрешения

Добавьте в настройки или при первом входе:

```typescript
if ('Notification' in window && Notification.permission === 'default') {
  Notification.requestPermission();
}
```

## 📊 Мониторинг

### Логи в консоли

```
WebSocket connected
New notification received: { type: "new_comment", message: "..." }
WebSocket disconnected
Attempting to reconnect WebSocket...
```

### Состояние подключения

```typescript
const { isConnected, connect, disconnect, send } = useWebSocketNotifications({...});

console.log('Connected:', isConnected);
```

## 🐛 Отладка

### Проверка подключения

```javascript
// В консоли браузера
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/notifications?token=YOUR_TOKEN');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
ws.onerror = (e) => console.error('Error:', e);
```

### Проверка Redis Pub/Sub (Backend)

```bash
# В терминале с Redis
redis-cli
SUBSCRIBE notifications:USER_ID

# В другом терминале
redis-cli
PUBLISH notifications:USER_ID '{"type":"test","message":"Test notification"}'
```

## 🚀 Производительность

### Оптимизации

1. **Debouncing:** Обновление UI происходит только при получении сообщения
2. **Lazy loading:** WebSocket подключается только для авторизованных пользователей
3. **Автоматическое отключение:** При unmount компонента
4. **Переиспользование соединения:** Одно WebSocket соединение на всё приложение

### Рекомендации

- Не создавайте несколько WebSocket подключений
- Используйте хук только в корневых компонентах (Header, App)
- Передавайте данные через props или context, а не создавайте новые подключения

## 📝 Примеры

### Пример 1: Показать toast при новом уведомлении

```typescript
useWebSocketNotifications({
  onMessage: (data) => {
    toast.success(data.message);
    loadNotifications();
  },
});
```

### Пример 2: Обновить конкретную проблему

```typescript
useWebSocketNotifications({
  onMessage: (data) => {
    if (data.type === 'status_changed' && data.problem_id === currentProblemId) {
      reloadProblem();
    }
  },
});
```

### Пример 3: Счетчик непрочитанных в реальном времени

```typescript
const [unreadCount, setUnreadCount] = useState(0);

useWebSocketNotifications({
  onMessage: () => {
    setUnreadCount(prev => prev + 1);
  },
});
```

## ✅ Готово!

WebSocket интеграция полностью настроена и работает в:
- ✅ Header (dropdown уведомлений)
- ✅ Notifications страница
- ✅ Browser notifications
- ✅ Автоматическое переподключение
- ✅ Real-time обновления

---

**Дата:** 2026-04-10
