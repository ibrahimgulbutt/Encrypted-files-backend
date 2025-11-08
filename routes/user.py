from fastapi import APIRouter, Depends, HTTPException, status, Request
from models.user import UserProfile, UserStorageStats, PasswordChange
from services.user_service import UserService
from services.auth_service import AuthService
from middleware.auth import require_auth
from middleware.rate_limit import apply_api_rate_limit
from utils.responses import APIResponse
from config.database import get_supabase
from models.auth import TokenData
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["User Profile"])

@router.get("/profile", response_model=dict, status_code=status.HTTP_200_OK)
@apply_api_rate_limit
async def get_user_profile(
    request: Request,
    current_user: TokenData = Depends(require_auth),
    supabase_client = Depends(get_supabase)
):
    """Get user profile information"""
    try:
        user_service = UserService(supabase_client)
        profile = await user_service.get_user_profile(current_user.user_id)
        
        return APIResponse.success(
            data={
                "id": profile.id,
                "email": profile.email,
                "created_at": profile.created_at.isoformat(),
                "storage_used": profile.storage_used,
                "storage_limit": profile.storage_limit,
                "storage_percentage": profile.storage_percentage,
                "total_files": profile.total_files,
                "last_login": profile.last_login.isoformat() if profile.last_login else None
            }
        )
        
    except ValueError as e:
        return APIResponse.not_found(message=str(e))
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        return APIResponse.internal_error(message="Failed to get user profile")

@router.get("/storage", response_model=dict, status_code=status.HTTP_200_OK)
@apply_api_rate_limit
async def get_storage_stats(
    request: Request,
    current_user: TokenData = Depends(require_auth),
    supabase_client = Depends(get_supabase)
):
    """Get storage statistics"""
    try:
        user_service = UserService(supabase_client)
        stats = await user_service.get_storage_stats(current_user.user_id)
        
        return APIResponse.success(
            data={
                "used": stats.used,
                "limit": stats.limit,
                "available": stats.available,
                "percentage": stats.percentage,
                "file_count": stats.file_count,
                "largest_file": stats.largest_file
            }
        )
        
    except ValueError as e:
        return APIResponse.not_found(message=str(e))
    except Exception as e:
        logger.error(f"Get storage stats error: {e}")
        return APIResponse.internal_error(message="Failed to get storage statistics")

@router.patch("/password", response_model=dict, status_code=status.HTTP_200_OK)
@apply_api_rate_limit
async def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: TokenData = Depends(require_auth),
    supabase_client = Depends(get_supabase)
):
    """Change password (requires old password)"""
    try:
        auth_service = AuthService(supabase_client)
        success = await auth_service.change_password(current_user.user_id, password_data)
        
        if success:
            return APIResponse.success(
                message="Password updated successfully"
            )
        else:
            return APIResponse.internal_error(message="Password change failed")
        
    except ValueError as e:
        if "invalid current password" in str(e).lower():
            return APIResponse.unauthorized(message="Current password is incorrect")
        else:
            return APIResponse.validation_error(message=str(e))
    except Exception as e:
        logger.error(f"Change password error: {e}")
        return APIResponse.internal_error(message="Password change failed")