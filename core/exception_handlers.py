from fastapi import Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from core.exceptions import DomainException
from starlette.websockets import WebSocketState

import logging
logger = logging.getLogger(__name__)



def register_exception_handlers(app):

    # =====================================================
    # DOMAIN EXCEPTION
    # =====================================================

    @app.exception_handler(DomainException)
    async def handle_domain_exception(
        request: Request | WebSocket,
        exc: DomainException,
    ):
        scope = request.scope

        logger.warning(
            "Erreur métier",
            extra={
                "path": scope.get("path", ""),
                "method": scope.get("method", ""),
                "status_code": exc.status_code,
                "error": exc.message,
            },
        )

        if isinstance(request, WebSocket):
            # Ne pas envoyer une seconde fermeture :
            # le refus peut déjà avoir été envoyé par Starlette.
            return None

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    # =====================================================
    # VALIDATION ERROR
    # =====================================================

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request | WebSocket,
        exc: RequestValidationError,
    ):
        scope = request.scope

        logger.warning(
            "Erreur de validation de requête",
            extra={
                "path": scope.get("path", ""),
                "method": scope.get("method", ""),
            },
        )

        if isinstance(request, WebSocket):
            if request.application_state == WebSocketState.CONNECTED:
                await request.close(code=1008)
            else:
                await request.close(code=1008)

            return None

        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {
                        "field": ".".join(map(str, err["loc"])),
                        "message": err["msg"],
                        "type": err["type"],
                    }
                    for err in exc.errors()
                ]
            },
        )

    # =====================================================
    # UNEXPECTED ERROR
    # =====================================================

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request | WebSocket,
        exc: Exception,
    ):
        scope = request.scope

        logger.exception(
            "Erreur interne inattendue",
            extra={
                "path": scope.get("path", ""),
                "method": scope.get("method", ""),
            },
        )

        if isinstance(request, WebSocket):
            if request.application_state == WebSocketState.CONNECTED:
                await request.close(code=1011)
            else:
                await request.close(code=1011)

            return None

        return JSONResponse(
            status_code=500,
            content={"detail": "INTERNAL_SERVER_ERROR"},
        )