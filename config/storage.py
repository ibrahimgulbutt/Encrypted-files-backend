from supabase import Client
from config.settings import settings
from config.database import get_supabase_authenticated
from typing import BinaryIO, Optional
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, supabase_client: Client, user_jwt_token: str = None):
        self.client = supabase_client
        self.bucket_name = settings.storage_bucket_name
        self.user_jwt_token = user_jwt_token
        
        # For now, just use the regular client since the bucket is public
        self.storage_client = supabase_client
    
    async def upload_file(
        self, 
        file_path: str, 
        file_data: BinaryIO, 
        content_type: str = "application/octet-stream"
    ) -> dict:
        """Upload encrypted file to Supabase Storage"""
        try:
            # Reset file pointer to beginning
            file_data.seek(0)
            
            # Read the file content as bytes
            file_content = file_data.read()
            
            # Reset file pointer again in case it's needed elsewhere
            file_data.seek(0)
            
            response = self.storage_client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": content_type}
            )
            logger.info(f"File uploaded successfully: {file_path}")
            return response
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            raise
    
    async def download_file(self, file_path: str) -> bytes:
        """Download encrypted file from Supabase Storage"""
        try:
            response = self.storage_client.storage.from_(self.bucket_name).download(file_path)
            logger.info(f"File downloaded successfully: {file_path}")
            return response
        except Exception as e:
            logger.error(f"Failed to download file {file_path}: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> dict:
        """Delete file from Supabase Storage"""
        try:
            response = self.storage_client.storage.from_(self.bucket_name).remove([file_path])
            logger.info(f"File deleted successfully: {file_path}")
            return response
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise
    
    async def create_signed_url(self, file_path: str, expires_in: int = 300) -> str:
        """Create a signed URL for file download"""
        try:
            response = self.storage_client.storage.from_(self.bucket_name).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            logger.info(f"Signed URL created for file: {file_path}")
            return response.get("signedURL")
        except Exception as e:
            logger.error(f"Failed to create signed URL for {file_path}: {e}")
            raise
    
    async def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file metadata from storage"""
        try:
            files = self.storage_client.storage.from_(self.bucket_name).list(
                path=file_path.rsplit("/", 1)[0] if "/" in file_path else ""
            )
            
            filename = file_path.rsplit("/", 1)[-1]
            for file_info in files:
                if file_info["name"] == filename:
                    return file_info
            
            return None
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            raise