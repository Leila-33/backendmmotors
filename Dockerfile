FROM python:3.11-slim

# --- environnement propre ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# --- dépendances système minimales ---
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- install python deps ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- copy code ---
COPY . .

# --- user non-root (important prod) ---
RUN useradd -m appuser
USER appuser

# default (overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]