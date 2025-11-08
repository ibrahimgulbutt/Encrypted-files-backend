from fastapi import APIRouter, Depends, HTTPException, status, Request
from models.user import UserCreate, UserLogin, PasswordChange
from models.auth import LoginResponse, RegisterResponse, TokenVerifyResponse
from services.auth_service import AuthService
from middleware.auth import require_auth
from middleware.rate_limit import apply_login_rate_limit, apply_register_rate_limit, limiter
from utils.responses import APIResponse
from config.database import get_supabase
from models.auth import TokenData
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
@apply_register_rate_limit
async def register(
    request: Request,
    user_data: UserCreate,
    supabase_client = Depends(get_supabase)
):
    """Register a new user"""
    try:
        auth_service = AuthService(supabase_client)
        result = await auth_service.register_user(user_data)
        
        return APIResponse.created(
            data={
                "user_id": result.user_id,
                "email": result.email,
                "created_at": result.created_at.isoformat()
            },
            message="User registered successfully"
        )
        
    except ValueError as e:
        if "already registered" in str(e):
            return APIResponse.conflict(message=str(e))
        else:
            return APIResponse.validation_error(message=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return APIResponse.internal_error(message="Registration failed")

@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
@apply_login_rate_limit
async def login(
    request: Request,
    login_data: UserLogin,
    supabase_client = Depends(get_supabase)
):
    """Authenticate user and get JWT token"""
    try:
        auth_service = AuthService(supabase_client)
        result = await auth_service.login_user(login_data)
        
        return APIResponse.success(
            data={
                "access_token": result.access_token,
                "token_type": result.token_type,
                "expires_in": result.expires_in,
                "user": result.user
            },
            message="Login successful"
        )
        
    except ValueError as e:
        return APIResponse.unauthorized(message="Invalid credentials")
    except Exception as e:
        logger.error(f"Login error: {e}")
        return APIResponse.internal_error(message="Login failed")

@router.post("/logout", response_model=dict, status_code=status.HTTP_200_OK)
async def logout(
    current_user: TokenData = Depends(require_auth)
):
    """Logout user (invalidate session)"""
    # Note: In a stateless JWT implementation, logout is handled client-side
    # by removing the token. For enhanced security, you could maintain a blacklist
    # of invalidated tokens in Redis or the database.
    
    logger.info(f"User logged out: {current_user.user_id}")
    
    return APIResponse.success(
        message="Logged out successfully"
    )

@router.post("/refresh", response_model=dict, status_code=status.HTTP_200_OK)
async def refresh_token(
    # Note: For now, we'll use the existing token to create a new one
    # In a production system, you'd implement proper refresh tokens
    current_user: TokenData = Depends(require_auth)
):
    """Refresh JWT token"""
    try:
        from utils.jwt import JWTManager
        
        # Create new access token
        new_token = JWTManager.create_access_token(
            current_user.user_id,
            current_user.email
        )
        
        return APIResponse.success(
            data={
                "access_token": new_token,
                "expires_in": JWTManager.get_token_expiry_seconds()
            }
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return APIResponse.internal_error(message="Token refresh failed")

@router.get("/verify", response_model=dict, status_code=status.HTTP_200_OK)
async def verify_token(
    current_user: TokenData = Depends(require_auth)
):
    """Verify if token is valid"""
    return APIResponse.success(
        data={
            "valid": True,
            "user_id": current_user.user_id,
            "expires_at": current_user.expires_at.isoformat() if current_user.expires_at else None
        }
    )