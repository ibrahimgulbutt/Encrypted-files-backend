from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="ZeroKnowledgeStorage", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Supabase
    supabase_url: str = Field(env="SUPABASE_URL")
    supabase_key: str = Field(env="SUPABASE_KEY")
    supabase_service_key: str = Field(env="SUPABASE_SERVICE_KEY")
    
    # JWT
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_minutes: int = Field(default=60, env="JWT_EXPIRATION_MINUTES")
    refresh_token_expiration_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRATION_DAYS")
    
    # Storage
    storage_bucket_name: str = Field(default="Files", env="STORAGE_BUCKET_NAME")
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    default_storage_limit_gb: int = Field(default=5, env="DEFAULT_STORAGE_LIMIT_GB")
    
    # Security
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # CORS
    allowed_origins: str = Field(default="http://localhost:3000", env="ALLOWED_ORIGINS")
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def default_storage_limit_bytes(self) -> int:
        return self.default_storage_limit_gb * 1024 * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()