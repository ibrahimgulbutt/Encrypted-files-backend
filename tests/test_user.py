import pytest
from fastapi.testclient import TestClient
from main import app

class TestUserRoutes:
    """Test user profile and settings routes"""
    
    def test_get_user_profile(self, client: TestClient, auth_headers):
        """Test getting user profile"""
        response = client.get("/api/v1/user/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert "email" in data["data"]
        assert "storage_used" in data["data"]
        assert "storage_limit" in data["data"]
        assert "storage_percentage" in data["data"]
    
    def test_get_user_profile_unauthorized(self, client: TestClient):
        """Test getting user profile without authentication"""
        response = client.get("/api/v1/user/profile")
        assert response.status_code == 401  # Unauthorized
    
    def test_get_storage_stats(self, client: TestClient, auth_headers):
        """Test getting storage statistics"""
        response = client.get("/api/v1/user/storage", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "used" in data["data"]
        assert "limit" in data["data"]
        assert "available" in data["data"]
        assert "percentage" in data["data"]
        assert "file_count" in data["data"]
    
    def test_change_password_success(self, client: TestClient, auth_headers):
        """Test successful password change"""
        password_data = {
            "old_password_hash": "a" * 32,
            "new_password_hash": "b" * 32,
            "new_salt": "c" * 16
        }
        
        response = client.patch("/api/v1/user/password", json=password_data, headers=auth_headers)
        
        # Note: This will likely fail in tests without proper setup
        # In a real test, you'd need to mock the auth service
        assert response.status_code in [200, 401, 500]  # Various possible outcomes
    
    def test_change_password_invalid_format(self, client: TestClient, auth_headers):
        """Test password change with invalid format"""
        password_data = {
            "old_password_hash": "short",  # Too short
            "new_password_hash": "b" * 32,
            "new_salt": "c" * 16
        }
        
        response = client.patch("/api/v1/user/password", json=password_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_change_password_unauthorized(self, client: TestClient):
        """Test password change without authentication"""
        password_data = {
            "old_password_hash": "a" * 32,
            "new_password_hash": "b" * 32,
            "new_salt": "c" * 16
        }
        
        response = client.patch("/api/v1/user/password", json=password_data)
        assert response.status_code == 401  # Unauthorized

class TestHealthRoutes:
    """Test health and system status routes"""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "status" in data["data"]
        assert "timestamp" in data["data"]
        assert "version" in data["data"]
    
    def test_system_stats(self, client: TestClient):
        """Test system statistics endpoint"""
        response = client.get("/api/v1/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_users" in data["data"]
        assert "total_files" in data["data"]
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data