import re
from typing import Any, Optional
from pydantic import EmailStr, ValidationError

class ValidationUtils:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_password_hash(password_hash: str) -> bool:
        """Validate password hash format and length"""
        return len(password_hash) >= 32 and isinstance(password_hash, str)
    
    @staticmethod
    def validate_salt(salt: str) -> bool:
        """Validate salt format and length"""
        return len(salt) >= 16 and isinstance(salt, str)
    
    @staticmethod
    def validate_file_size(size: int, max_size: int) -> bool:
        """Validate file size"""
        return isinstance(size, int) and 0 < size <= max_size
    
    @staticmethod
    def validate_uuid(uuid_string: str) -> bool:
        """Validate UUID format"""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, uuid_string.lower()))
    
    @staticmethod
    def validate_base64(base64_string: str) -> bool:
        """Validate base64 encoded string"""
        import base64
        try:
            base64.b64decode(base64_string)
            return True
        except Exception:
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for storage"""
        # Remove path traversal attempts and invalid characters
        filename = re.sub(r'[<>:"|?*]', '_', filename)
        filename = filename.replace('..', '_')
        filename = filename.replace('/', '_')
        filename = filename.replace('\\', '_')
        return filename[:255]  # Limit length
    
    @staticmethod
    def validate_pagination_params(page: int, limit: int) -> tuple[bool, str]:
        """Validate pagination parameters"""
        if not isinstance(page, int) or page < 1:
            return False, "Page must be a positive integer"
        
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            return False, "Limit must be between 1 and 100"
        
        return True, ""
    
    @staticmethod
    def validate_sort_params(sort_by: str, order: str) -> tuple[bool, str]:
        """Validate sorting parameters"""
        valid_sort_fields = ['uploaded_at', 'file_size', 'encrypted_filename']
        valid_orders = ['asc', 'desc']
        
        if sort_by not in valid_sort_fields:
            return False, f"Invalid sort field. Must be one of: {valid_sort_fields}"
        
        if order.lower() not in valid_orders:
            return False, "Order must be 'asc' or 'desc'"
        
        return True, ""

class SecurityValidator:
    @staticmethod
    def validate_file_upload(file_data: bytes, max_size: int) -> tuple[bool, str]:
        """Validate uploaded file"""
        if not file_data:
            return False, "File data is empty"
        
        if len(file_data) > max_size:
            return False, f"File size exceeds maximum allowed size of {max_size} bytes"
        
        return True, ""
    
    @staticmethod
    def validate_content_type(content_type: str) -> bool:
        """Validate content type for security"""
        dangerous_types = [
            'application/x-executable',
            'application/x-msdownload',
            'application/x-dosexec'
        ]
        
        return content_type not in dangerous_types