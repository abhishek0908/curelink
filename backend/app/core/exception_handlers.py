from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import AppException
from app.schema.response import APIResponse
import logging

logger = logging.getLogger(__name__)

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error_response(code=exc.code, message=exc.message).model_dump(),
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error_response(code="HTTP_ERROR", message=str(exc.detail)).model_dump(),
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    message = "Validation Error"
    if errors:
        first_error = errors[0]
        # loc is usually ("body", "email"), etc.
        loc_parts = [str(x) for x in first_error.get("loc", []) if x not in ("body", "query", "path")]
        field = ".".join(loc_parts)
        msg = first_error.get("msg", "")
        message = f"{field}: {msg}" if field else msg

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse.error_response(code="VALIDATION_ERROR", message=message).model_dump(),
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse.error_response(code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred").model_dump(),
    )
