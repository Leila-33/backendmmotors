# app/core/config.py
from pydantic_settings import BaseSettings


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
    S3_ENDPOINT: str | None = None
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str
    S3_REGION: str = "us-east-1"

    class Config:
        env_file = ".env"


# instance globale
settings = Settings()