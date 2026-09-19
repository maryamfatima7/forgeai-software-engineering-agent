import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ForgeAIError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: object | None = None) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def _error_response(code: str, message: str, details: object | None = None) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": {"code": code, "message": message, "details": details}})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ForgeAIError)
    async def handle_forge_error(request: Request, exc: ForgeAIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response("validation_error", "The request did not pass validation.", exc.errors())

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error", extra={"path": request.url.path})
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "An internal error occurred."}},
        )
