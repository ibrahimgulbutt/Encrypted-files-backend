from supabase import Client
from models.user import UserProfile, UserStorageStats, UserDB
from models.file import FileDB
from config.settings import settings
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile information"""
        try:
            # Get user data
            user_result = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if not user_result.data:
                raise ValueError("User not found")
            
            user_data = user_result.data[0]
            user = UserDB(**user_data)
            
            # Get file count
            files_result = self.client.table("files").select("id").eq("user_id", user_id).eq("is_deleted", False).execute()
            total_files = len(files_result.data) if files_result.data else 0
            
            # Calculate storage percentage
            storage_percentage = (user.storage_used / user.storage_limit) * 100 if user.storage_limit > 0 else 0
            
            return UserProfile(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
                storage_used=user.storage_used,
                storage_limit=user.storage_limit,
                storage_percentage=round(storage_percentage, 2),
                total_files=total_files,
                last_login=user.last_login
            )
            
        except ValueError as e:
            logger.warning(f"User profile error: {e}")
            raise
        except Exception as e:
            logger.error(f"Get user profile error: {e}")
            raise Exception("Failed to get user profile")
    
    async def get_storage_stats(self, user_id: str) -> UserStorageStats:
        """Get detailed storage statistics for user"""
        try:
            # Get user data
            user_result = self.client.table("users").select("storage_used, storage_limit").eq("id", user_id).execute()
            
            if not user_result.data:
                raise ValueError("User not found")
            
            user_data = user_result.data[0]
            storage_used = user_data["storage_used"]
            storage_limit = user_data["storage_limit"]
            
            # Get file statistics
            files_result = self.client.table("files").select("file_size, encrypted_filename").eq("user_id", user_id).eq("is_deleted", False).execute()
            
            files_data = files_result.data if files_result.data else []
            file_count = len(files_data)
            
            # Find largest file
            largest_file = None
            if files_data:
                largest = max(files_data, key=lambda x: x["file_size"])
                largest_file = {
                    "id": largest.get("id"),
                    "encrypted_filename": largest["encrypted_filename"],
                    "size": largest["file_size"]
                }
            
            # Calculate available storage
            available = max(0, storage_limit - storage_used)
            percentage = (storage_used / storage_limit) * 100 if storage_limit > 0 else 0
            
            return UserStorageStats(
                used=storage_used,
                limit=storage_limit,
                available=available,
                percentage=round(percentage, 2),
                file_count=file_count,
                largest_file=largest_file
            )
            
        except ValueError as e:
            logger.warning(f"Storage stats error: {e}")
            raise
        except Exception as e:
            logger.error(f"Get storage stats error: {e}")
            raise Exception("Failed to get storage statistics")
    
    async def update_storage_used(self, user_id: str, size_delta: int) -> bool:
        """Update user's storage usage (can be positive or negative)"""
        try:
            # Get current storage usage
            user_result = self.client.table("users").select("storage_used, storage_limit").eq("id", user_id).execute()
            
            if not user_result.data:
                raise ValueError("User not found")
            
            current_used = user_result.data[0]["storage_used"]
            storage_limit = user_result.data[0]["storage_limit"]
            
            new_used = max(0, current_used + size_delta)
            
            # Check if new usage exceeds limit (for uploads)
            if size_delta > 0 and new_used > storage_limit:
                raise ValueError("Storage quota exceeded")
            
            # Update storage usage
            self.client.table("users").update({
                "storage_used": new_used
            }).eq("id", user_id).execute()
            
            logger.debug(f"Storage updated for user {user_id}: {current_used} -> {new_used}")
            return True
            
        except ValueError as e:
            logger.warning(f"Storage update error: {e}")
            raise
        except Exception as e:
            logger.error(f"Update storage error: {e}")
            raise Exception("Failed to update storage usage")
    
    async def check_storage_quota(self, user_id: str, file_size: int) -> bool:
        """Check if user has enough storage quota for a file"""
        try:
            user_result = self.client.table("users").select("storage_used, storage_limit").eq("id", user_id).execute()
            
            if not user_result.data:
                return False
            
            storage_used = user_result.data[0]["storage_used"]
            storage_limit = user_result.data[0]["storage_limit"]
            
            return (storage_used + file_size) <= storage_limit
            
        except Exception as e:
            logger.error(f"Storage quota check error: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserDB]:
        """Get user by ID"""
        try:
            user_result = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if not user_result.data:
                return None
            
            return UserDB(**user_result.data[0])
            
        except Exception as e:
            logger.error(f"Get user by ID error: {e}")
            return None
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            self.client.table("users").update({
                "is_active": False
            }).eq("id", user_id).execute()
            
            logger.info(f"User deactivated: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"User deactivation error: {e}")
            return False