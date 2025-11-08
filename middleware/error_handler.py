from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from utils.responses import APIResponse
from pydantic import ValidationError
import logging
import traceback

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return APIResponse.internal_error(
        message="An unexpected error occurred"
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    # If detail is already in our API format, return it directly
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                **exc.detail
            }
        )
    
    # Convert standard HTTP exceptions to our format
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED", 
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        413: "PAYLOAD_TOO_LARGE",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_code = error_codes.get(exc.status_code, "UNKNOWN_ERROR")
    
    return APIResponse.error(
        code=error_code,
        message=str(exc.detail),
        status_code=exc.status_code
    )

async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return APIResponse.validation_error(
        message="Validation failed",
        details={"validation_errors": errors}
    )

async def request_validation_exception_handler(request: Request, exc):
    """Handle FastAPI request validation errors"""
    logger.warning(f"Request validation error: {exc}")
    
    return APIResponse.validation_error(
        message="Invalid request data",
        details={"error": str(exc)}
    )

class ErrorMiddleware:
    @staticmethod
    def setup_handlers(app):
        """Setup all exception handlers"""
        app.add_exception_handler(Exception, global_exception_handler)
        app.add_exception_handler(HTTPException, http_exception_handler)
        app.add_exception_handler(ValidationError, validation_exception_handler)
        
        # Handle FastAPI's RequestValidationError
        try:
            from fastapi.exceptions import RequestValidationError
            app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
        except ImportError:
            logger.warning("RequestValidationError not available")
        
        logger.info("Exception handlers registered")