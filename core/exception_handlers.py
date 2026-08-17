from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from core.exceptions import DomainException
import logging

logger = logging.getLogger(__name__)


def register_exception_handlers(app):

    # =========================
    # DOMAIN EXCEPTION
    # =========================

    @app.exception_handler(DomainException)
    async def handle_domain_exception(
        request: Request,
        exc: DomainException,
    ):

        logger.warning(
            "Erreur métier",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message
            },
        )


    # =========================
    # VALIDATION ERROR
    # =========================

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ):

        logger.warning(
            "Erreur de validation de requête",
            extra={
                "path": request.url.path,
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {
                        "field": ".".join(
                            map(str, err["loc"])
                        ),
                        "message": err["msg"],
                        "type": err["type"],
                    }
                    for err in exc.errors()
                ]
            },
        )


    # =========================
    # UNEXPECTED ERROR
    # =========================

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ):

        logger.exception(
            "Erreur interne inattendue",
            extra={
                "path": request.url.path,
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "INTERNAL_SERVER_ERROR"
            },
        )