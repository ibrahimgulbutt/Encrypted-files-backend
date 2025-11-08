import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app
import os

# Test configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
TEST_JWT_SECRET = "test-secret-key-for-testing-purposes-only"

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Create an async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    """Create authorization headers for testing"""
    # This would create a test JWT token
    from utils.jwt import JWTManager
    import os
    
    # Override JWT secret for testing
    original_secret = os.getenv("JWT_SECRET_KEY")
    os.environ["JWT_SECRET_KEY"] = TEST_JWT_SECRET
    
    test_token = JWTManager.create_access_token("test-user-id", "test@example.com")
    
    # Restore original secret
    if original_secret:
        os.environ["JWT_SECRET_KEY"] = original_secret
    
    return {"Authorization": f"Bearer {test_token}"}

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password_hash": "a" * 32,  # 32 char hash
        "salt": "b" * 16  # 16 char salt
    }

@pytest.fixture
def sample_file_metadata():
    """Sample file metadata for testing"""
    return {
        "encrypted_size": "encrypted_size_value",
        "encrypted_type": "encrypted_type_value", 
        "encrypted_original_name": "encrypted_name_value"
    }

class TestConfig:
    """Test configuration class"""
    TESTING = True
    JWT_SECRET_KEY = TEST_JWT_SECRET