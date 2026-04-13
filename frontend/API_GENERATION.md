# API Client Generation

## Генерация API клиента

Для генерации TypeScript клиента из OpenAPI спецификации используйте:

```bash
npm run generate-api
```

Эта команда:
1. Генерирует API клиент из `../backend/openapi.json`
2. Автоматически применяет патчи для совместимости с браузером

## Что патчится автоматически

После генерации скрипт `scripts/post-generate-api.sh` автоматически исправляет:

1. **Удаление Node.js FormData импорта**
   - Генератор добавляет `import FormData from 'form-data'` (Node.js пакет)
   - В браузере используется нативный `FormData`
   - Патч удаляет этот импорт

2. **Исправление FormData.getHeaders()**
   - Генератор использует `formData.getHeaders()` (метод Node.js)
   - В браузере `FormData` не имеет этого метода
   - Патч заменяет на пустой объект

## Axios Interceptors

API клиент использует глобальные axios interceptors из `src/api/client.ts`:

- **Request Interceptor**: автоматически добавляет JWT токен в заголовок
- **Response Interceptor**: автоматически обновляет истёкший токен через refresh token

Все сгенерированные сервисы автоматически используют эти interceptors.

## Структура

```
src/api/
├── client.ts                    # Axios interceptors и конфигурация
├── generated/                   # Сгенерированный код (не редактировать вручную!)
│   ├── core/
│   │   ├── OpenAPI.ts
│   │   └── request.ts          # Патчится автоматически
│   ├── models/
│   └── services/
└── ...
```

## Важно

⚠️ **НЕ редактируйте файлы в `src/api/generated/` вручную!**

Все изменения будут потеряны при следующей генерации. Если нужны изменения:
1. Обновите `scripts/post-generate-api.sh`
2. Или внесите изменения в `src/api/client.ts`
