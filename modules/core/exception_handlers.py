from fastapi import Request
from fastapi.responses import JSONResponse
from modules.core.exceptions import DomainException


def register_exception_handlers(app):

    @app.exception_handler(DomainException)
    def handle_domain_exception(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(Exception)
    def handle_unexpected_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "INTERNAL_SERVER_ERROR"}
        )