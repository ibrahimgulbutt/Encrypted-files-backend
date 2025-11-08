from typing import Any, Optional, Dict
from fastapi import status
from fastapi.responses import JSONResponse

class APIResponse:
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation successful",
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """Create a successful API response"""
        response_data = {
            "success": True,
            "message": message
        }
        
        if data is not None:
            response_data["data"] = data
            
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    @staticmethod
    def error(
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create an error API response"""
        response_data = {
            "success": False,
            "error": {
                "code": code,
                "message": message
            }
        }
        
        if details:
            response_data["error"]["details"] = details
            
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully"
    ) -> JSONResponse:
        """Create a 201 Created response"""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Unauthorized access"
    ) -> JSONResponse:
        """Create a 401 Unauthorized response"""
        return APIResponse.error(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(
        message: str = "Access forbidden"
    ) -> JSONResponse:
        """Create a 403 Forbidden response"""
        return APIResponse.error(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found"
    ) -> JSONResponse:
        """Create a 404 Not Found response"""
        return APIResponse.error(
            code="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def conflict(
        message: str = "Resource conflict"
    ) -> JSONResponse:
        """Create a 409 Conflict response"""
        return APIResponse.error(
            code="CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )
    
    @staticmethod
    def validation_error(
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create a 422 Validation Error response"""
        return APIResponse.error(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )
    
    @staticmethod
    def payload_too_large(
        message: str = "Payload too large"
    ) -> JSONResponse:
        """Create a 413 Payload Too Large response"""
        return APIResponse.error(
            code="PAYLOAD_TOO_LARGE",
            message=message,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )
    
    @staticmethod
    def rate_limited(
        message: str = "Rate limit exceeded"
    ) -> JSONResponse:
        """Create a 429 Rate Limited response"""
        return APIResponse.error(
            code="RATE_LIMITED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    @staticmethod
    def internal_error(
        message: str = "Internal server error"
    ) -> JSONResponse:
        """Create a 500 Internal Server Error response"""
        return APIResponse.error(
            code="INTERNAL_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )