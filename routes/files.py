from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query, Request
from models.file import FileUpload, FileResponse, FileListResult, FileQueryParams, FileDeleteResponse, FileDownloadResponse, FileMetadata
from services.file_service import FileService
from middleware.auth import require_auth
from middleware.rate_limit import apply_upload_rate_limit, apply_download_rate_limit, apply_api_rate_limit
from utils.responses import APIResponse
from config.database import get_supabase
from models.auth import TokenData
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["File Management"])

@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
@apply_upload_rate_limit
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    encrypted_filename: str = Form(...),
    encrypted_metadata: str = Form(...),
    file_size: int = Form(...),
    current_user: TokenData = Depends(require_auth),
    supabase_client = Depends(get_supabase)
):
    """Upload encrypted file"""
    try:
        # Parse encrypted metadata
        try:
            metadata_dict = json.loads(encrypted_metadata)
            metadata = FileMetadata(**metadata_dict)
        except (json.JSONDecodeError, ValueError) as e:
            return APIResponse.validation_error(message="Invalid metadata format")
        
        # Create file upload model
        file_upload = FileUpload(
            encrypted_filename=encrypted_filename,
            encrypted_metadata=metadata,
            file_size=file_size
        )
        
        # Upload file
        file_service = FileService(supabase_client)
        result = await file_service.upload_file(
            user_id=current_user.user_id,
            file_data=file_upload,
            file_content=file.file,
            content_type=file.content_type or "application/octet-stream"
        )
        
        return APIResponse.created(
            data={
                "file_id": result.id,
                "uploaded_at": result.uploaded_at.isoformat(),
                "storage_path": f"{current_user.user_id}/{result.id}.enc",
                "file_size": result.file_size
            },
            message="File uploaded successfully"
        )
        
    except ValueError as e:
        if "quota exceeded" in str(e).lower():
            return APIResponse.error(
                code="STORAGE_QUOTA_EXCEEDED",
                message=str(e),
                status_code=status.HTTP_402_PAYMENT_REQUIRED
            )
        elif "file size" in str(e).lower():
            return APIResponse.payload_too_large(message=str(e))
        else:
            return APIResponse.validation_error(message=str(e))
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return APIResponse.internal_error(message="File upload failed")

@router.get("", response_model=dict, status_code=status.HTTP_200_OK)
@apply_api_rate_limit
async def list_files(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="uploaded_at"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    current_user: TokenData = Depends(require_auth),
    supabase_client = Depends(get_supabase)
):
    """List all user's files (paginated)"""
    try:
        query_params = FileQueryParams(
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        file_service = FileService(supabase_client)
        result = await file_service.list_user_files(current_user.user_id, query_params)
        
        # Convert to response format
        files_data = []
        for file_item in result.files:
            files_data.append({
                "id": file_item.id,
                "encrypted_filename": file_item.encrypted_filename,
                "encrypted_metadata": file_item.encrypted_metadata,
                "file_size": file_item.file_size,
                "uploaded_at": file_item.uploaded_at.isoformat(),
                "last_accessed": file_item.last_accessed.isoformat() if file_item.last_accessed else None
            })
        
        return APIResponse.success(
            data={
                "files": files_data,
                "pagination": {
                    "total": result.pagination.total,
                    "page": result.pagination.page,
                    "limit": result.pagination.limit,
                    "total_pages": result.pagination.total_pages
                }
            }
        )
        
    except ValueError as e:
        return APIResponse.validation_error(message=str(e))
    except Exception as e:
        logger.error(f"List files error: {e}")
        return APIResponse.internal_error(message="Failed to list files")

@router.get("/{file_id}", response_model=dict, status_code=status.HTTP_200_OK)
@apply_api_rate_limit
async def get_file_metadata(
    request: Request,
    file_id: str,
    current_user: TokenData = Depends(require_auth),
    supabase_client = Depends(get_supabase)
):
    """Get file metadata"""
    try:
        file_service = FileService(supabase_client)
        result = await file_service.get_file_metadata(current_user.user_id, file_id)
        
        if not result:
            return APIResponse.not_found(message="File not found")
        
        return APIResponse.success(
            data={
                "id": result.id,
                "encrypted_filename": result.encrypted_filename,
                "encrypted_metadata": result.encrypted_metadata,
                "file_size": result.file_size,
                "uploaded_at": result.uploaded_at.isoformat(),
                "encryption_algorithm": result.encryption_algorithm
            }
        )
        
    except ValueError as e:
        return APIResponse.validation_error(message=str(e))
    except Exception as e:
        logger.error(f"Get file metadata error: {e}")
        return APIResponse.internal_error(message="Failed to get file metadata")

@router.get("/{file_id}/download", response_model=dict, status_code=status.HTTP_200_OK)
@apply_download_rate_limit
async def download_file(
    request: Request,
    file_id: str,
    current_user: TokenData = Depends(require_auth),
    supabase_client = Depends(get_supabase)
):
    """Download encrypted file (returns pre-signed URL)"""
    try:
        file_service = FileService(supabase_client)
        result = await file_service.download_file(current_user.user_id, file_id)
        
        if not result:
            return APIResponse.not_found(message="File not found")
        
        return APIResponse.success(
            data={
                "download_url": result.download_url,
                "expires_in": result.expires_in
            }
        )
        
    except ValueError as e:
        return APIResponse.validation_error(message=str(e))
    except Exception as e:
        logger.error(f"File download error: {e}")
        return APIResponse.internal_error(message="File download failed")

@router.delete("/{file_id}", response_model=dict, status_code=status.HTTP_200_OK)
@apply_api_rate_limit
async def delete_file(
    request: Request,
    file_id: str,
    current_user: TokenData = Depends(require_auth),
    supabase_client = Depends(get_supabase)
):
    """Delete file (soft delete)"""
    try:
        file_service = FileService(supabase_client)
        result = await file_service.delete_file(current_user.user_id, file_id, permanent=False)
        
        return APIResponse.success(
            data={
                "file_id": result.file_id,
                "deleted_at": result.deleted_at.isoformat()
            },
            message="File deleted successfully"
        )
        
    except ValueError as e:
        if "not found" in str(e).lower():
            return APIResponse.not_found(message=str(e))
        else:
            return APIResponse.validation_error(message=str(e))
    except Exception as e:
        logger.error(f"File delete error: {e}")
        return APIResponse.internal_error(message="File deletion failed")

@router.delete("/{file_id}/permanent", response_model=dict, status_code=status.HTTP_200_OK)
@apply_api_rate_limit
async def permanently_delete_file(
    request: Request,
    file_id: str,
    current_user: TokenData = Depends(require_auth),
    supabase_client = Depends(get_supabase)
):
    """Permanently delete file (hard delete)"""
    try:
        file_service = FileService(supabase_client)
        result = await file_service.delete_file(current_user.user_id, file_id, permanent=True)
        
        return APIResponse.success(
            message="File permanently deleted"
        )
        
    except ValueError as e:
        if "not found" in str(e).lower():
            return APIResponse.not_found(message=str(e))
        else:
            return APIResponse.validation_error(message=str(e))
    except Exception as e:
        logger.error(f"Permanent file delete error: {e}")
        return APIResponse.internal_error(message="File deletion failed")