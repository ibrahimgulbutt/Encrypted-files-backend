import pytest
from fastapi.testclient import TestClient
from main import app
from tests.conftest import TestConfig

class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_register_success(self, client: TestClient, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data["data"]
        assert data["data"]["email"] == sample_user_data["email"]
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email"""
        invalid_data = {
            "email": "invalid-email",
            "password_hash": "a" * 32,
            "salt": "b" * 16
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_duplicate_email(self, client: TestClient, sample_user_data):
        """Test registration with duplicate email"""
        # First registration
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Second registration with same email
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 409  # Conflict
    
    def test_login_success(self, client: TestClient, sample_user_data):
        """Test successful login"""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login
        login_data = {
            "email": sample_user_data["email"],
            "password_hash": sample_user_data["password_hash"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "Bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, sample_user_data):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com", 
            "password_hash": "wrong_hash"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401  # Unauthorized
    
    def test_verify_token_valid(self, client: TestClient, auth_headers):
        """Test token verification with valid token"""
        response = client.get("/api/v1/auth/verify", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["valid"] is True
    
    def test_verify_token_missing(self, client: TestClient):
        """Test token verification without token"""
        response = client.get("/api/v1/auth/verify")
        assert response.status_code == 401  # Unauthorized
    
    def test_logout(self, client: TestClient, auth_headers):
        """Test logout endpoint"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "logged out" in data["message"].lower()
    
    def test_refresh_token(self, client: TestClient, auth_headers):
        """Test token refresh"""
        response = client.post("/api/v1/auth/refresh", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]

class TestAuthValidation:
    """Test authentication validation and security"""
    
    def test_weak_password_hash(self, client: TestClient):
        """Test registration with weak password hash"""
        weak_data = {
            "email": "test@example.com",
            "password_hash": "short",  # Too short
            "salt": "b" * 16
        }
        
        response = client.post("/api/v1/auth/register", json=weak_data)
        assert response.status_code == 422  # Validation error
    
    def test_short_salt(self, client: TestClient):
        """Test registration with short salt"""
        weak_data = {
            "email": "test@example.com", 
            "password_hash": "a" * 32,
            "salt": "short"  # Too short
        }
        
        response = client.post("/api/v1/auth/register", json=weak_data)
        assert response.status_code == 422  # Validation error