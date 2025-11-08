from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password_hash: str = Field(..., min_length=32, description="Client-side hashed password")
    salt: str = Field(..., min_length=16, description="Random salt from client")

class UserLogin(BaseModel):
    email: EmailStr
    password_hash: str = Field(..., min_length=32, description="Client-side hashed password")

class UserResponse(UserBase):
    id: str = Field(..., description="User UUID")
    created_at: datetime
    storage_used: int = Field(default=0, description="Storage used in bytes")
    storage_limit: int = Field(description="Storage limit in bytes")
    total_files: Optional[int] = Field(default=0)
    last_login: Optional[datetime] = None

class UserProfile(UserResponse):
    storage_percentage: float = Field(description="Storage used percentage")

class UserStorageStats(BaseModel):
    used: int = Field(description="Storage used in bytes")
    limit: int = Field(description="Storage limit in bytes")
    available: int = Field(description="Available storage in bytes")
    percentage: float = Field(description="Storage used percentage")
    file_count: int = Field(description="Number of files")
    largest_file: Optional[Dict[str, Any]] = None

class PasswordChange(BaseModel):
    old_password_hash: str = Field(..., min_length=32)
    new_password_hash: str = Field(..., min_length=32)
    new_salt: str = Field(..., min_length=16)

# Database models
class UserDB(BaseModel):
    id: str
    email: str
    password_hash: str
    salt: str
    created_at: datetime
    storage_used: int = 0
    storage_limit: int
    is_active: bool = True
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True