from supabase import Client
from config.storage import StorageService
from typing import BinaryIO, Optional
import logging

logger = logging.getLogger(__name__)

class StorageServiceWrapper:
    """Wrapper service for Supabase Storage operations"""
    
    def __init__(self, supabase_client: Client):
        self.storage_service = StorageService(supabase_client)
    
    async def upload_encrypted_file(
        self, 
        user_id: str, 
        file_id: str, 
        file_data: BinaryIO,
        content_type: str = "application/octet-stream"
    ) -> dict:
        """Upload encrypted file to storage"""
        try:
            storage_path = f"{user_id}/{file_id}.enc"
            return await self.storage_service.upload_file(
                file_path=storage_path,
                file_data=file_data,
                content_type=content_type
            )
        except Exception as e:
            logger.error(f"Storage upload error: {e}")
            raise
    
    async def download_encrypted_file(
        self, 
        user_id: str, 
        file_id: str
    ) -> bytes:
        """Download encrypted file from storage"""
        try:
            storage_path = f"{user_id}/{file_id}.enc"
            return await self.storage_service.download_file(storage_path)
        except Exception as e:
            logger.error(f"Storage download error: {e}")
            raise
    
    async def delete_encrypted_file(
        self, 
        user_id: str, 
        file_id: str
    ) -> dict:
        """Delete encrypted file from storage"""
        try:
            storage_path = f"{user_id}/{file_id}.enc"
            return await self.storage_service.delete_file(storage_path)
        except Exception as e:
            logger.error(f"Storage delete error: {e}")
            raise
    
    async def create_download_url(
        self, 
        user_id: str, 
        file_id: str,
        expires_in: int = 300
    ) -> str:
        """Create signed download URL"""
        try:
            storage_path = f"{user_id}/{file_id}.enc"
            return await self.storage_service.create_signed_url(storage_path, expires_in)
        except Exception as e:
            logger.error(f"Storage signed URL error: {e}")
            raise
    
    async def get_file_info(
        self, 
        user_id: str, 
        file_id: str
    ) -> Optional[dict]:
        """Get file information from storage"""
        try:
            storage_path = f"{user_id}/{file_id}.enc"
            return await self.storage_service.get_file_info(storage_path)
        except Exception as e:
            logger.error(f"Storage file info error: {e}")
            return None
    
    def generate_storage_path(self, user_id: str, file_id: str) -> str:
        """Generate storage path for file"""
        return f"{user_id}/{file_id}.enc"