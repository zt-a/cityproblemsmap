from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(  
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore", 
    )
    # === Database ===
    TEST_DATABASE_URL: str = ""
    DATABASE_URL: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # === Redis ===
    REDIS_URL: str
    TEST_REDIS_URL: str | None = None

    TESTING: bool = False

    # === JWT ===
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    ALLOW_ORIGINS: str = "http://localhost:5173"


    # Хранилище медиа — "local" или "cloudinary"
    MEDIA_STORAGE: str = "local"

    # Локальное хранилище
    MEDIA_LOCAL_DIR: str = "media"   # папка в корне проекта
    MEDIA_BASE_URL:  str = "http://localhost:8000/media"

    # Cloudinary (нужны только если MEDIA_STORAGE=cloudinary)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY:    str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Лимиты
    MAX_IMAGE_SIZE_MB: int = 30
    MAX_VIDEO_SIZE_MB: int = 200

    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"
    ALLOWED_VIDEO_TYPES: str = "video/mp4,video/quicktime,video/avi"

    SMTP_HOST:     str = "smtp.gmail.com"
    SMTP_PORT:     int = 587
    SMTP_USER:     str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM:     str = ""

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Reset password token
    RESET_PASSWORD_EXPIRE_MINUTES: int = 60

    # Sentry monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0  # 100% в dev, 0.1 в prod

    # CAPTCHA (Google reCAPTCHA v3)
    RECAPTCHA_SECRET_KEY: str = ""
    RECAPTCHA_SITE_KEY: str = ""

    # Альтернативные CAPTCHA (опционально)
    HCAPTCHA_SECRET_KEY: str = ""
    HCAPTCHA_SITE_KEY: str = ""
    TURNSTILE_SECRET_KEY: str = ""
    TURNSTILE_SITE_KEY: str = ""

    @property
    def allow_origins_list(self) -> list[str]:
        """Возвращает список разрешённых origin для CORS"""
        return [origin.strip() for origin in self.ALLOW_ORIGINS.split(",")]


    @property
    def db_url(self) -> str:
        """
        Универсальный Database URL:
        - TESTING → TEST_DATABASE_URL
        - иначе → DATABASE_URL (docker/prod)
        """
        if self.TESTING and self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL

        return self.DATABASE_URL


    @property
    def redis_url(self) -> str:
        """
        Универсальный Redis URL:
        - TESTING → TEST_REDIS_URL
        - иначе → REDIS_URL (docker/prod)
        """
        if self.TESTING and self.TEST_REDIS_URL:
            return self.TEST_REDIS_URL

        return self.REDIS_URL

        


# Singleton instance
settings = Settings()