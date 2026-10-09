from fastapi import FastAPI, Request
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from core.logging_config import setup_logging
import core.database.import_models
from sqlalchemy.orm import configure_mappers
from core.exception_handlers import register_exception_handlers
from api.routes import api_router
import sentry_sdk
from core.config.settings import settings
logger = logging.getLogger(__name__)

configure_mappers()
setup_logging()


# =========================
# SENTRY INITIALIZATION
# =========================

if settings.sentry_dsn:

    sentry_sdk.init(

        dsn=settings.sentry_dsn,

        environment=(
            settings.sentry_environment
        ),

        traces_sample_rate=(
            settings.sentry_traces_sample_rate
        ),
    )

# =========================
# APP INIT (ONLY ONCE)
# =========================
from contextlib import asynccontextmanager

import asyncio
import threading


from core.scheduler.scheduler import (
    start_scheduler,
    stop_scheduler,
)

from modules.vehicles.infrastructure.queue.redis_listener import (
    start_redis_listener,
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API starting...")

    start_scheduler()

    loop = asyncio.get_running_loop()

    thread = threading.Thread(
        target=start_redis_listener,
        args=(loop,),
        daemon=True,
        name="redis-listener",
    )
    thread.start()

    yield

    stop_scheduler()
    logger.info("API shutting down")



app = FastAPI(
    lifespan=lifespan
)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://mmotors.e-mecaformation.com",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =========================
# ROUTES
# =========================
app.include_router(api_router, prefix="/api")

# =========================
# EXCEPTION HANDLERS
# =========================
register_exception_handlers(app)


@app.exception_handler(ValidationError)
async def handler(request: Request, exc: ValidationError):

    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "field": ".".join(map(str, err["loc"])),
                    "message": err["msg"],
                    "type": err["type"]
                }
                for err in exc.errors()
            ]
        }
    )




