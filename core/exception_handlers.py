from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from core.exceptions import DomainException
import logging

logger = logging.getLogger(__name__)

def register_exception_handlers(app):


    @app.exception_handler(DomainException)
    async def handle_domain_exception(
        request: Request,
        exc: DomainException
    ):

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message
            }
        )


    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError
    ):

        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {
                        "field": ".".join(
                            map(str, err["loc"])
                        ),
                        "message": err["msg"],
                        "type": err["type"]
                    }
                    for err in exc.errors()
                ]
            }
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception
    ):

        logger.exception(exc)

        return JSONResponse(
            status_code=500,
            content={
                "detail": "INTERNAL_SERVER_ERROR"
            }
        )