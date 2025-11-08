import time
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

class RateLimitMiddleware:
    @staticmethod
    def get_limiter() -> Limiter:
        return limiter
    
    @staticmethod
    def login_rate_limit():
        """Rate limit for login attempts: 5 per 15 minutes per IP"""
        return "5/15minutes"
    
    @staticmethod
    def upload_rate_limit():
        """Rate limit for file uploads: 20 per hour per user"""
        return "20/hour"
    
    @staticmethod
    def download_rate_limit():
        """Rate limit for file downloads: 100 per hour per user"""
        return "100/hour"
    
    @staticmethod
    def api_rate_limit():
        """Rate limit for general API requests: 1000 per hour per user"""
        return "1000/hour"
    
    @staticmethod
    def register_rate_limit():
        """Rate limit for registration: 3 per hour per IP"""
        return "3/hour"

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    logger.warning(f"Rate limit exceeded for IP: {get_remote_address(request)}")
    
    response = HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": {
                "code": "RATE_LIMITED",
                "message": "Rate limit exceeded. Please try again later.",
                "retry_after": exc.retry_after if hasattr(exc, 'retry_after') else 60
            }
        }
    )
    return response

# Rate limiting decorators for different endpoints
def apply_login_rate_limit(func):
    """Decorator for login rate limiting"""
    return limiter.limit(RateLimitMiddleware.login_rate_limit())(func)

def apply_upload_rate_limit(func):
    """Decorator for upload rate limiting"""
    return limiter.limit(RateLimitMiddleware.upload_rate_limit())(func)

def apply_download_rate_limit(func):
    """Decorator for download rate limiting"""
    return limiter.limit(RateLimitMiddleware.download_rate_limit())(func)

def apply_api_rate_limit(func):
    """Decorator for general API rate limiting"""
    return limiter.limit(RateLimitMiddleware.api_rate_limit())(func)

def apply_register_rate_limit(func):
    """Decorator for registration rate limiting"""
    return limiter.limit(RateLimitMiddleware.register_rate_limit())(func)