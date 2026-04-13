# CityProblemMap Frontend

Современный dark-themed dashboard для системы отслеживания городских проблем.

## 🚀 Технологический стек

- **React 18** + **TypeScript**
- **Vite** - быстрый dev server и сборка
- **Tailwind CSS** - utility-first CSS framework
- **React Router** - клиентский роутинг
- **TanStack Query** - управление серверным состоянием и кеширование
- **Zustand** - легковесный state management
- **Leaflet** - интерактивные карты
- **Axios** - HTTP клиент
- **React Hook Form + Zod** - формы и валидация
- **Lucide React** - иконки
- **date-fns** - работа с датами

## 📋 Требования

- Node.js >= 18
- pnpm >= 8
- Backend API запущен на http://localhost:8000

## 🛠 Установка

```bash
# Установить зависимости
pnpm install
```

## 🏃 Запуск

```bash
# Development сервер
pnpm dev

# Откроется на http://localhost:3000
```

## 🏗 Сборка

```bash
# Production сборка
pnpm build

# Preview production сборки
pnpm preview
```

## 📁 Структура проекта

```
src/
├── api/                    # API клиенты
│   ├── client.ts          # Axios instance с interceptors
│   └── generated/         # Автогенерированные типы из OpenAPI
├── components/            # React компоненты
│   ├── layout/           # Layout компоненты
│   │   ├── Sidebar.tsx
│   │   └── MainLayout.tsx
│   ├── problem/          # Компоненты проблем
│   │   ├── ProblemCard.tsx
│   │   ├── ProblemList.tsx
│   │   └── ProblemDetail.tsx
│   ├── map/              # Компоненты карты
│   │   └── MapView.tsx
│   ├── comments/         # Компоненты комментариев
│   └── ui/               # Базовые UI компоненты
├── pages/                # Страницы приложения
│   └── HomePage.tsx
├── hooks/                # Custom React hooks
├── store/                # Zustand stores
├── types/                # TypeScript типы
│   └── api.ts
├── utils/                # Утилиты
├── App.tsx               # Главный компонент
├── main.tsx              # Entry point
└── index.css             # Глобальные стили
```

## 🎨 Дизайн система

### Цвета (Dark Theme)

```css
Background: #0B1220
Card: #111827
Primary: #3B82F6
Success: #10B981
Warning: #F59E0B
Danger: #EF4444
```

### Layout

- **Sidebar** - фиксированная боковая панель (88px)
- **Top Section** (60% высоты) - Problem List + Map
- **Bottom Section** (40% высоты) - Problem Detail (YouTube-style)

### Компоненты

- **ProblemCard** - карточка проблемы с hover эффектами
- **MapView** - темная карта с цветными маркерами
- **ProblemDetail** - YouTube-style layout для детального просмотра

## 🔌 API Integration

Backend API: `http://localhost:8000/api/v1`

Основные эндпоинты:
- `/auth/*` - авторизация
- `/problems/*` - проблемы
- `/zones/*` - зоны/районы
- `/users/*` - пользователи
- `/comments/*` - комментарии

WebSocket: `ws://localhost:8000/api/v1/ws/notifications`

## 🧪 Разработка

### Добавление новой страницы

1. Создать компонент в `src/pages/`
2. Добавить роут в `src/App.tsx`
3. Добавить пункт в Sidebar (если нужно)

### Работа с API

```typescript
import { apiClient } from '@/api/client'

// GET запрос
const response = await apiClient.get('/problems')

// POST запрос
const response = await apiClient.post('/problems', data)
```

### Использование TanStack Query

```typescript
import { useQuery } from '@tanstack/react-query'

const { data, isLoading } = useQuery({
  queryKey: ['problems'],
  queryFn: () => apiClient.get('/problems').then(res => res.data)
})
```

## 📝 TODO

- [ ] Добавить авторизацию (login/register)
- [ ] Реализовать создание проблемы
- [ ] Подключить реальный API вместо mock данных
- [ ] Добавить WebSocket для real-time уведомлений
- [ ] Реализовать фильтры и поиск
- [ ] Добавить пагинацию
- [ ] Реализовать профиль пользователя
- [ ] Добавить панель модератора
- [ ] Добавить панель официальных лиц
- [ ] Мобильная адаптация

## 🐛 Известные проблемы

- Mock данные вместо реального API
- Карта использует placeholder координаты
- Комментарии без полной вложенности

## 📚 Полезные ссылки

- [Backend API Docs](http://localhost:8000/docs)
- [OpenAPI Spec](../backend/openapi.json)
- [Design Mockup](./DesignFrontend.png)
- [Memory Files](../.claude/projects/.../memory/)

## 👥 Команда

Разработано с помощью Claude Code

---

**Дата создания:** 2026-04-10
**Версия:** 0.1.0
