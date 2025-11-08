from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class FileMetadata(BaseModel):
    encrypted_size: str = Field(description="Encrypted file size")
    encrypted_type: str = Field(description="Encrypted file type")
    encrypted_original_name: str = Field(description="Encrypted original filename")

class FileUpload(BaseModel):
    encrypted_filename: str = Field(..., description="Base64 encrypted filename")
    encrypted_metadata: FileMetadata
    file_size: int = Field(..., gt=0, description="Actual file size in bytes for quota check")

class FileResponse(BaseModel):
    id: str = Field(description="File UUID")
    encrypted_filename: str
    encrypted_metadata: FileMetadata
    file_size: int
    uploaded_at: datetime
    last_accessed: Optional[datetime] = None
    encryption_algorithm: str = Field(default="AES-256-GCM")

class FileListResponse(BaseModel):
    id: str
    encrypted_filename: str
    encrypted_metadata: FileMetadata
    file_size: int
    uploaded_at: datetime
    last_accessed: Optional[datetime] = None

class FileDownloadResponse(BaseModel):
    download_url: str = Field(description="Pre-signed URL for file download")
    expires_in: int = Field(description="URL expiration time in seconds")

class FilePagination(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int

class FileListResult(BaseModel):
    files: List[FileListResponse]
    pagination: FilePagination

class FileQueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="uploaded_at")
    order: str = Field(default="desc", pattern="^(asc|desc)$")

class FileDeleteResponse(BaseModel):
    file_id: str
    deleted_at: datetime

# Database models
class FileDB(BaseModel):
    id: str
    user_id: str
    encrypted_filename: str
    encrypted_metadata: Dict[str, Any]
    file_size: int
    storage_path: str
    uploaded_at: datetime
    last_accessed: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    encryption_algorithm: str = "AES-256-GCM"
    
    class Config:
        from_attributes = True