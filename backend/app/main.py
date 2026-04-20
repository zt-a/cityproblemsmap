# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.config import settings
from app.api import router as api_router
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler  # noqa: F401
from slowapi.errors import RateLimitExceeded
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.middleware.security import SecurityHeadersMiddleware
from app.websocket.notifications import websocket_notifications
from app.websocket.problems import websocket_problem
import sentry_sdk
from starlette.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse

# Инициализация Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        enable_tracing=True,
    )



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Синхронный init_db безопасно запускаем в пуле потоков
    await run_in_threadpool(init_db)

    # Создание тестовых аккаунтов
    from app.utils.create_test_accounts import create_all_test_accounts
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        await run_in_threadpool(create_all_test_accounts, db)
    finally:
        db.close()

    # Создание папки для медиа тоже синхронная операция — можно напрямую
    Path(settings.MEDIA_LOCAL_DIR).mkdir(exist_ok=True)

    # Генерация openapi.json при запуске
    import json
    openapi_schema = app.openapi()
    openapi_path = Path(__file__).parent.parent / "openapi.json"
    with open(openapi_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
    print(f"✅ OpenAPI schema generated: {openapi_path}")

    yield


app = FastAPI(
    title="City Problems Map",
    description="Digital Twin города — карта городских проблем",
    version="0.1.0",
    lifespan=lifespan,

    redoc_url=None,
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins_list,   # список разрешённых доменов
    allow_credentials=True,
    allow_methods=["*"],     # GET, POST, PUT, DELETE и т.д.
    allow_headers=["*"],     # разрешённые заголовки
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

if settings.MEDIA_STORAGE == "local":
    app.mount(
        "/media",
        StaticFiles(directory=settings.MEDIA_LOCAL_DIR),
        name="media",
    )

@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Redoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <redoc spec-url="/openapi.json"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """)

app.include_router(api_router)

# WebSocket endpoints
app.websocket("/api/v1/ws/notifications")(websocket_notifications)
app.websocket("/api/v1/ws/problems/{problem_id}")(websocket_problem)
