from jose import jwt, JWTError
from datetime import datetime, timedelta
from config.settings import settings
from models.auth import JWTPayload, TokenData
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        """Create a new JWT access token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=settings.jwt_expiration_minutes)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": expire,
            "iat": now,
            "sub": user_id
        }
        
        try:
            token = jwt.encode(
                payload,
                settings.jwt_secret_key,
                algorithm=settings.jwt_algorithm
            )
            logger.debug(f"JWT token created for user: {user_id}")
            return token
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            
            user_id = payload.get("user_id")
            email = payload.get("email")
            exp = payload.get("exp")
            
            if not user_id or not email:
                logger.warning("Invalid token: missing user data")
                return None
            
            expires_at = datetime.fromtimestamp(exp) if exp else None
            
            return TokenData(
                user_id=user_id,
                email=email,
                expires_at=expires_at
            )
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            return None
    
    @staticmethod
    def is_token_expired(token_data: TokenData) -> bool:
        """Check if token is expired"""
        if not token_data.expires_at:
            return True
        return datetime.utcnow() > token_data.expires_at
    
    @staticmethod
    def get_token_expiry_seconds() -> int:
        """Get token expiration time in seconds"""
        return settings.jwt_expiration_minutes * 60