from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

import core.database.import_models

from sqlalchemy.orm import configure_mappers

configure_mappers()



# seulement après
from core.exception_handlers import register_exception_handlers
from api.routes import api_router

from dotenv import load_dotenv
load_dotenv()



# =========================
# APP INIT (ONLY ONCE)
# =========================
from fastapi import FastAPI
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


    print("🚀 API starting...")


    # Scheduler

    start_scheduler()



    # Redis listener

    loop = asyncio.get_event_loop()


    thread = threading.Thread(
        target=start_redis_listener,
        args=(loop,),
        daemon=True
    )

    thread.start()


    print("🔥 Redis listener started")


    yield



    stop_scheduler()


    print("🛑 API shutting down")



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




