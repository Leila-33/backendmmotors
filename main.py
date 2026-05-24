from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

import infrastructure.db.import_models
from modules.core.exception_handlers import register_exception_handlers
from api.routes import api_router

# =========================
# APP INIT
# =========================
app = FastAPI()

register_exception_handlers(app)

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTES
# =========================
app.include_router(api_router, prefix="/api")

# =========================
# VALIDATION ERROR HANDLER
# =========================
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

