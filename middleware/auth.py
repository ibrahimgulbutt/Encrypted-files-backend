from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import JWTManager
from utils.responses import APIResponse
from models.auth import TokenData
from typing import Optional
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

class AuthMiddleware:
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> TokenData:
        """Extract and validate JWT token from Authorization header"""
        try:
            token = credentials.credentials
            token_data = JWTManager.verify_token(token)
            
            if not token_data:
                logger.warning("Invalid token provided")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
            if JWTManager.is_token_expired(token_data):
                logger.warning(f"Expired token for user: {token_data.user_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            logger.debug(f"Authenticated user: {token_data.user_id}")
            return token_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    @staticmethod
    async def get_optional_user(
        request: Request
    ) -> Optional[TokenData]:
        """Extract user from token if present, but don't require authentication"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            token_data = JWTManager.verify_token(token)
            
            if token_data and not JWTManager.is_token_expired(token_data):
                return token_data
            
            return None
            
        except Exception as e:
            logger.debug(f"Optional auth failed: {e}")
            return None

# Dependency for requiring authentication
async def require_auth(
    current_user: TokenData = Depends(AuthMiddleware.get_current_user)
) -> TokenData:
    return current_user

# Dependency for optional authentication
async def optional_auth(
    request: Request
) -> Optional[TokenData]:
    return await AuthMiddleware.get_optional_user(request)