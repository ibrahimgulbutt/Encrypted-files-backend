from fastapi import APIRouter, status
from utils.responses import APIResponse
from config.database import get_supabase
from config.settings import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Health & System"])

@router.get("/health", response_model=dict, status_code=status.HTTP_200_OK)
async def health_check():
    """Check API health"""
    try:
        # Test database connection
        database_status = "connected"
        try:
            supabase_client = get_supabase()
            # Simple test query
            result = supabase_client.table("users").select("count", count="exact").limit(0).execute()
            if result.count is None:
                database_status = "error"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            database_status = "error"
        
        # Test storage connection
        storage_status = "connected"
        try:
            # Test storage bucket access
            bucket_list = supabase_client.storage.list_buckets()
            if not any(bucket.name == settings.storage_bucket_name for bucket in bucket_list):
                storage_status = "bucket_not_found"
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            storage_status = "error"
        
        return APIResponse.success(
            data={
                "status": "healthy" if database_status == "connected" and storage_status == "connected" else "degraded",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": settings.app_version,
                "database": database_status,
                "storage": storage_status
            }
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return APIResponse.internal_error(message="Health check failed")

@router.get("/stats", response_model=dict, status_code=status.HTTP_200_OK)
async def get_system_stats():
    """Get system statistics (admin only - for future implementation)"""
    try:
        # Note: This would require admin authentication in a real implementation
        supabase_client = get_supabase()
        
        # Get total users
        users_result = supabase_client.table("users").select("count", count="exact").execute()
        total_users = users_result.count or 0
        
        # Get total files
        files_result = supabase_client.table("files").select("count", count="exact").eq("is_deleted", False).execute()
        total_files = files_result.count or 0
        
        # Get total storage used
        storage_result = supabase_client.table("users").select("storage_used").execute()
        total_storage_used = sum(user["storage_used"] for user in (storage_result.data or []))
        
        # Active sessions would require session tracking implementation
        active_sessions = 0  # Placeholder
        
        return APIResponse.success(
            data={
                "total_users": total_users,
                "total_files": total_files,
                "total_storage_used": total_storage_used,
                "active_sessions": active_sessions
            }
        )
        
    except Exception as e:
        logger.error(f"System stats error: {e}")
        return APIResponse.internal_error(message="Failed to get system statistics")