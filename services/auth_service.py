from supabase import Client
from models.user import UserCreate, UserLogin, UserDB, PasswordChange
from models.auth import LoginResponse, RegisterResponse, TokenResponse
from utils.jwt import JWTManager
from utils.validators import ValidationUtils
from config.settings import settings
from datetime import datetime
import uuid
import logging
import hashlib
import secrets
import hmac

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        # Use a more reliable hashing approach instead of bcrypt
        self.hash_iterations = 100000  # PBKDF2 iterations
    
    def _hash_password(self, password_hash: str, salt: str) -> str:
        """Securely hash password using PBKDF2"""
        # Combine client password hash with salt
        combined = f"{password_hash}:{salt}"
        
        # Generate a random salt for PBKDF2
        pbkdf2_salt = secrets.token_bytes(32)
        
        # Hash using PBKDF2
        password_key = hashlib.pbkdf2_hmac(
            'sha256', 
            combined.encode('utf-8'), 
            pbkdf2_salt, 
            self.hash_iterations
        )
        
        # Return salt + hash (base64 encoded for storage)
        import base64
        salt_and_hash = pbkdf2_salt + password_key
        return base64.b64encode(salt_and_hash).decode('utf-8')
    
    def _verify_password(self, password_hash: str, salt: str, stored_hash: str) -> bool:
        """Verify password using PBKDF2"""
        try:
            import base64
            
            # Decode stored hash
            salt_and_hash = base64.b64decode(stored_hash.encode('utf-8'))
            
            # Extract salt (first 32 bytes) and hash (remaining bytes)
            pbkdf2_salt = salt_and_hash[:32]
            stored_password_key = salt_and_hash[32:]
            
            # Combine client password hash with salt
            combined = f"{password_hash}:{salt}"
            
            # Hash the provided password with the same salt
            password_key = hashlib.pbkdf2_hmac(
                'sha256',
                combined.encode('utf-8'),
                pbkdf2_salt,
                self.hash_iterations
            )
            
            # Use constant-time comparison
            return hmac.compare_digest(password_key, stored_password_key)
            
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    async def register_user(self, user_data: UserCreate) -> RegisterResponse:
        """Register a new user"""
        try:
            # Validate input
            if not ValidationUtils.validate_email(user_data.email):
                raise ValueError("Invalid email format")
            
            if not ValidationUtils.validate_password_hash(user_data.password_hash):
                raise ValueError("Invalid password hash format")
            
            if not ValidationUtils.validate_salt(user_data.salt):
                raise ValueError("Invalid salt format")
            
            # Check if user already exists
            existing_user = self.client.table("users").select("id").eq("email", user_data.email).execute()
            if existing_user.data:
                raise ValueError("Email already registered")
            
            # Create user ID
            user_id = str(uuid.uuid4())
            
            # Hash the already hashed password for additional security using PBKDF2
            final_password_hash = self._hash_password(user_data.password_hash, user_data.salt)
            logger.info("Password successfully hashed using PBKDF2")
            
            # Create user record
            user_record = {
                "id": user_id,
                "email": user_data.email,
                "password_hash": final_password_hash,
                "salt": user_data.salt,
                "created_at": datetime.utcnow().isoformat(),
                "storage_used": 0,
                "storage_limit": settings.default_storage_limit_bytes,
                "is_active": True
            }
            
            result = self.client.table("users").insert(user_record).execute()
            
            if not result.data:
                raise Exception("Failed to create user")
            
            logger.info(f"User registered successfully: {user_data.email}")
            
            return RegisterResponse(
                user_id=user_id,
                email=user_data.email,
                created_at=datetime.utcnow()
            )
            
        except ValueError as e:
            logger.warning(f"Registration validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise Exception("Registration failed")
    
    async def login_user(self, login_data: UserLogin) -> LoginResponse:
        """Authenticate user and return JWT token"""
        try:
            # Get user from database
            user_result = self.client.table("users").select("*").eq("email", login_data.email).execute()
            
            if not user_result.data:
                raise ValueError("Invalid credentials")
            
            user_data = user_result.data[0]
            user = UserDB(**user_data)
            
            if not user.is_active:
                raise ValueError("Account is not active")
            
            # Verify password using PBKDF2
            if not self._verify_password(login_data.password_hash, user.salt, user.password_hash):
                raise ValueError("Invalid credentials")
            
            # Update last login
            self.client.table("users").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user.id).execute()
            
            # Create JWT token
            access_token = JWTManager.create_access_token(user.id, user.email)
            
            logger.info(f"User logged in successfully: {user.email}")
            
            return LoginResponse(
                access_token=access_token,
                token_type="Bearer",
                expires_in=JWTManager.get_token_expiry_seconds(),
                user={
                    "id": user.id,
                    "email": user.email,
                    "storage_used": user.storage_used,
                    "storage_limit": user.storage_limit
                }
            )
            
        except ValueError as e:
            logger.warning(f"Login failed for {login_data.email}: {e}")
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise Exception("Login failed")
    
    async def change_password(self, user_id: str, password_data: PasswordChange) -> bool:
        """Change user password"""
        try:
            # Get current user
            user_result = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if not user_result.data:
                raise ValueError("User not found")
            
            user = UserDB(**user_result.data[0])
            
            # Verify old password using PBKDF2
            if not self._verify_password(password_data.old_password_hash, user.salt, user.password_hash):
                raise ValueError("Invalid current password")
            
            # Validate new password
            if not ValidationUtils.validate_password_hash(password_data.new_password_hash):
                raise ValueError("Invalid new password hash format")
            
            if not ValidationUtils.validate_salt(password_data.new_salt):
                raise ValueError("Invalid new salt format")
            
            # Hash new password using PBKDF2
            new_password_hash = self._hash_password(password_data.new_password_hash, password_data.new_salt)
            
            # Update password
            self.client.table("users").update({
                "password_hash": new_password_hash,
                "salt": password_data.new_salt
            }).eq("id", user_id).execute()
            
            logger.info(f"Password changed for user: {user_id}")
            return True
            
        except ValueError as e:
            logger.warning(f"Password change error for user {user_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Password change error: {e}")
            raise Exception("Password change failed")
    
    async def verify_user_exists(self, user_id: str) -> bool:
        """Verify if user exists and is active"""
        try:
            user_result = self.client.table("users").select("is_active").eq("id", user_id).execute()
            
            if not user_result.data:
                return False
            
            return user_result.data[0]["is_active"]
            
        except Exception as e:
            logger.error(f"User verification error: {e}")
            return False
    
    async def get_user_by_email(self, email: str) -> UserDB:
        """Get user by email address"""
        try:
            user_result = self.client.table("users").select("*").eq("email", email).execute()
            
            if not user_result.data:
                return None
            
            return UserDB(**user_result.data[0])
            
        except Exception as e:
            logger.error(f"Get user by email error: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> UserDB:
        """Get user by email address"""
        try:
            user_result = self.client.table("users").select("*").eq("email", email).execute()
            
            if not user_result.data:
                return None
            
            return UserDB(**user_result.data[0])
            
        except Exception as e:
            logger.error(f"Get user by email error: {e}")
            return None