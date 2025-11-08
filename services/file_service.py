from supabase import Client
from models.file import FileUpload, FileResponse, FileListResult, FileQueryParams, FileDeleteResponse, FileDB, FilePagination, FileDownloadResponse
from config.storage import StorageService
from services.user_service import UserService
from utils.validators import ValidationUtils, SecurityValidator
from config.settings import settings
from datetime import datetime
from typing import List, Optional, BinaryIO
import uuid
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.storage_service = StorageService(supabase_client)
        self.user_service = UserService(supabase_client)
    
    async def upload_file(
        self, 
        user_id: str, 
        file_data: FileUpload, 
        file_content: BinaryIO,
        content_type: str = "application/octet-stream"
    ) -> FileResponse:
        """Upload encrypted file"""
        try:
            # Validate file size
            if not ValidationUtils.validate_file_size(file_data.file_size, settings.max_file_size_bytes):
                raise ValueError(f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB")
            
            # Check storage quota
            if not await self.user_service.check_storage_quota(user_id, file_data.file_size):
                raise ValueError("Storage quota exceeded")
            
            # Validate file content
            file_bytes = file_content.read()
            file_content.seek(0)  # Reset pointer
            
            is_valid, error_msg = SecurityValidator.validate_file_upload(file_bytes, settings.max_file_size_bytes)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Generate file ID and storage path
            file_id = str(uuid.uuid4())
            storage_path = f"{user_id}/{file_id}.enc"
            
            # Upload to storage
            upload_result = await self.storage_service.upload_file(
                file_path=storage_path,
                file_data=file_content,
                content_type=content_type
            )
            
            # Create file record in database
            file_record = {
                "id": file_id,
                "user_id": user_id,
                "encrypted_filename": file_data.encrypted_filename,
                "encrypted_metadata": file_data.encrypted_metadata.dict(),
                "file_size": file_data.file_size,
                "storage_path": storage_path,
                "uploaded_at": datetime.utcnow().isoformat(),
                "is_deleted": False,
                "encryption_algorithm": "AES-256-GCM"
            }
            
            db_result = self.client.table("files").insert(file_record).execute()
            
            if not db_result.data:
                # Cleanup storage if database insert failed
                try:
                    await self.storage_service.delete_file(storage_path)
                except:
                    pass
                raise Exception("Failed to save file metadata")
            
            # Update user storage usage
            await self.user_service.update_storage_used(user_id, file_data.file_size)
            
            logger.info(f"File uploaded successfully: {file_id} for user {user_id}")
            
            return FileResponse(
                id=file_id,
                encrypted_filename=file_data.encrypted_filename,
                encrypted_metadata=file_data.encrypted_metadata,
                file_size=file_data.file_size,
                uploaded_at=datetime.utcnow(),
                encryption_algorithm="AES-256-GCM"
            )
            
        except ValueError as e:
            logger.warning(f"File upload validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"File upload error: {e}")
            raise Exception("File upload failed")
    
    async def list_user_files(self, user_id: str, params: FileQueryParams) -> FileListResult:
        """List user's files with pagination"""
        try:
            # Validate pagination parameters
            is_valid, error_msg = ValidationUtils.validate_pagination_params(params.page, params.limit)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Validate sort parameters
            is_valid, error_msg = ValidationUtils.validate_sort_params(params.sort_by, params.order)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Calculate offset
            offset = (params.page - 1) * params.limit
            
            # Build query
            query = self.client.table("files").select("*").eq("user_id", user_id).eq("is_deleted", False)
            
            # Add sorting
            if params.order.lower() == "desc":
                query = query.order(params.sort_by, desc=True)
            else:
                query = query.order(params.sort_by)
            
            # Get total count
            count_result = self.client.table("files").select("id", count="exact").eq("user_id", user_id).eq("is_deleted", False).execute()
            total_count = count_result.count if count_result.count is not None else 0
            
            # Get paginated results
            result = query.range(offset, offset + params.limit - 1).execute()
            
            files_data = result.data if result.data else []
            
            # Convert to response models
            files = []
            for file_data in files_data:
                files.append(FileResponse(
                    id=file_data["id"],
                    encrypted_filename=file_data["encrypted_filename"],
                    encrypted_metadata=file_data["encrypted_metadata"],
                    file_size=file_data["file_size"],
                    uploaded_at=datetime.fromisoformat(file_data["uploaded_at"].replace("Z", "+00:00")),
                    last_accessed=datetime.fromisoformat(file_data["last_accessed"].replace("Z", "+00:00")) if file_data.get("last_accessed") else None,
                    encryption_algorithm=file_data.get("encryption_algorithm", "AES-256-GCM")
                ))
            
            # Calculate pagination info
            total_pages = (total_count + params.limit - 1) // params.limit
            
            pagination = FilePagination(
                total=total_count,
                page=params.page,
                limit=params.limit,
                total_pages=total_pages
            )
            
            return FileListResult(files=files, pagination=pagination)
            
        except ValueError as e:
            logger.warning(f"File list validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"List files error: {e}")
            raise Exception("Failed to list files")
    
    async def get_file_metadata(self, user_id: str, file_id: str) -> Optional[FileResponse]:
        """Get file metadata"""
        try:
            if not ValidationUtils.validate_uuid(file_id):
                raise ValueError("Invalid file ID format")
            
            file_result = self.client.table("files").select("*").eq("id", file_id).eq("user_id", user_id).eq("is_deleted", False).execute()
            
            if not file_result.data:
                return None
            
            file_data = file_result.data[0]
            
            # Update last accessed timestamp
            self.client.table("files").update({
                "last_accessed": datetime.utcnow().isoformat()
            }).eq("id", file_id).execute()
            
            return FileResponse(
                id=file_data["id"],
                encrypted_filename=file_data["encrypted_filename"],
                encrypted_metadata=file_data["encrypted_metadata"],
                file_size=file_data["file_size"],
                uploaded_at=datetime.fromisoformat(file_data["uploaded_at"].replace("Z", "+00:00")),
                last_accessed=datetime.utcnow(),
                encryption_algorithm=file_data.get("encryption_algorithm", "AES-256-GCM")
            )
            
        except ValueError as e:
            logger.warning(f"Get file metadata error: {e}")
            raise
        except Exception as e:
            logger.error(f"Get file metadata error: {e}")
            return None
    
    async def download_file(self, user_id: str, file_id: str) -> Optional[FileDownloadResponse]:
        """Get download URL for file"""
        try:
            if not ValidationUtils.validate_uuid(file_id):
                raise ValueError("Invalid file ID format")
            
            # Get file metadata
            file_result = self.client.table("files").select("storage_path").eq("id", file_id).eq("user_id", user_id).eq("is_deleted", False).execute()
            
            if not file_result.data:
                return None
            
            storage_path = file_result.data[0]["storage_path"]
            
            # Create signed URL (5 minute expiry)
            signed_url = await self.storage_service.create_signed_url(storage_path, expires_in=300)
            
            # Update last accessed timestamp
            self.client.table("files").update({
                "last_accessed": datetime.utcnow().isoformat()
            }).eq("id", file_id).execute()
            
            logger.info(f"Download URL created for file: {file_id}")
            
            return FileDownloadResponse(
                download_url=signed_url,
                expires_in=300
            )
            
        except ValueError as e:
            logger.warning(f"File download error: {e}")
            raise
        except Exception as e:
            logger.error(f"File download error: {e}")
            return None
    
    async def delete_file(self, user_id: str, file_id: str, permanent: bool = False) -> FileDeleteResponse:
        """Delete file (soft or hard delete)"""
        try:
            if not ValidationUtils.validate_uuid(file_id):
                raise ValueError("Invalid file ID format")
            
            # Get file metadata
            file_result = self.client.table("files").select("*").eq("id", file_id).eq("user_id", user_id).execute()
            
            if not file_result.data:
                raise ValueError("File not found")
            
            file_data = file_result.data[0]
            
            if permanent or file_data.get("is_deleted", False):
                # Hard delete - remove from storage and database
                try:
                    await self.storage_service.delete_file(file_data["storage_path"])
                except Exception as e:
                    logger.warning(f"Failed to delete file from storage: {e}")
                
                # Remove from database
                self.client.table("files").delete().eq("id", file_id).execute()
                
                # Update user storage usage
                await self.user_service.update_storage_used(user_id, -file_data["file_size"])
                
                logger.info(f"File permanently deleted: {file_id}")
            else:
                # Soft delete - mark as deleted
                self.client.table("files").update({
                    "is_deleted": True,
                    "deleted_at": datetime.utcnow().isoformat()
                }).eq("id", file_id).execute()
                
                logger.info(f"File soft deleted: {file_id}")
            
            return FileDeleteResponse(
                file_id=file_id,
                deleted_at=datetime.utcnow()
            )
            
        except ValueError as e:
            logger.warning(f"File delete error: {e}")
            raise
        except Exception as e:
            logger.error(f"File delete error: {e}")
            raise Exception("File deletion failed")