from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # =========================
    # APP
    # =========================
    APP_NAME: str = "My SaaS API"

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

    redis_host: str = "redis"
    redis_port: int = 6379

    # =========================
    # EMAIL
    # =========================
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

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


    STRIPE_SECRET_KEY: str
    STRIPE_PUBLIC_KEY: str
    STRIPE_WEBHOOK_SECRET: str



    # =========================
    # STRIPE REDIRECT URLS
    # =========================
    SUCCESS_URL: str
    CANCEL_URL: str
    
    class Config:
        env_file = ".env"

    # =========================
    # SENTRY
    # =========================

    sentry_dsn: str | None = None

    sentry_environment: str = "development"

    sentry_traces_sample_rate: float = 0.1


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    
# instance globale
settings = Settings()