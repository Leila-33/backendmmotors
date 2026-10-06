from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =========================
    # APP
    # =========================
    APP_NAME: str = "M-Motors API"
    environment: str = "development"

    # =========================
    # JWT
    # =========================
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # =========================
    # DATABASE
    # =========================
    DATABASE_URL: str
    DB_HOST: str

    # =========================
    # REDIS
    # =========================
    redis_host: str = "redis"
    redis_port: int = 6379

    # =========================
    # EMAIL
    # =========================
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    FRONTEND_URL: str = "http://localhost:3000"

    # =========================
    # S3 / MINIO
    # =========================
    S3_ENDPOINT: str
    S3_PUBLIC_ENDPOINT: str
    S3_BUCKET: str
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    # =========================
    # STRIPE
    # =========================
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLIC_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    SUCCESS_URL: str
    CANCEL_URL: str

    # =========================
    # SENTRY
    # =========================
    sentry_dsn: str | None = None
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1

    # =========================
    # COOKIE
    # =========================
    @property
    def cookie_secure(self) -> bool:
        return self.environment.lower() == "production"

    # =========================
    # CONFIGURATION
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()