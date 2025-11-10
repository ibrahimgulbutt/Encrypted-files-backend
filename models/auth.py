from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class TokenData(BaseModel):
    user_id: str
    email: str
    expires_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(description="Token expiration in seconds")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    expires_in: int

class TokenVerifyResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    expires_at: Optional[datetime] = None

class RegisterResponse(BaseModel):
    user_id: str
    email: str
    created_at: datetime

class GetSaltRequest(BaseModel):
    email: EmailStr

class GetSaltResponse(BaseModel):
    success: bool
    data: Dict[str, str]

# JWT Payload model for internal use
class JWTPayload(BaseModel):
    user_id: str
    email: str
    exp: int
    iat: int
    sub: str  # subject (user_id)