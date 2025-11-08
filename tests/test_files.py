import pytest
from fastapi.testclient import TestClient
from main import app
from io import BytesIO
import json

class TestFileRoutes:
    """Test file management routes"""
    
    def test_upload_file_success(self, client: TestClient, auth_headers, sample_file_metadata):
        """Test successful file upload"""
        # Create test file data
        test_file_content = b"encrypted file content for testing"
        
        files = {
            "file": ("test.enc", BytesIO(test_file_content), "application/octet-stream")
        }
        
        data = {
            "encrypted_filename": "encrypted_filename_base64",
            "encrypted_metadata": json.dumps(sample_file_metadata),
            "file_size": len(test_file_content)
        }
        
        response = client.post(
            "/api/v1/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["success"] is True
        assert "file_id" in result["data"]
    
    def test_upload_file_too_large(self, client: TestClient, auth_headers, sample_file_metadata):
        """Test upload with file too large"""
        files = {
            "file": ("large.enc", BytesIO(b"x" * 100), "application/octet-stream")
        }
        
        # Report much larger size than actual
        data = {
            "encrypted_filename": "encrypted_filename_base64",
            "encrypted_metadata": json.dumps(sample_file_metadata),
            "file_size": 60 * 1024 * 1024  # 60MB (exceeds 50MB limit)
        }
        
        response = client.post(
            "/api/v1/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 413  # Payload too large
    
    def test_upload_file_unauthorized(self, client: TestClient, sample_file_metadata):
        """Test file upload without authentication"""
        files = {
            "file": ("test.enc", BytesIO(b"test"), "application/octet-stream")
        }
        
        data = {
            "encrypted_filename": "encrypted_filename_base64",
            "encrypted_metadata": json.dumps(sample_file_metadata),
            "file_size": 4
        }
        
        response = client.post("/api/v1/files/upload", files=files, data=data)
        assert response.status_code == 401  # Unauthorized
    
    def test_list_files_success(self, client: TestClient, auth_headers):
        """Test listing files"""
        response = client.get("/api/v1/files", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "files" in data["data"]
        assert "pagination" in data["data"]
    
    def test_list_files_with_pagination(self, client: TestClient, auth_headers):
        """Test listing files with pagination parameters"""
        params = {
            "page": 1,
            "limit": 10,
            "sort_by": "uploaded_at",
            "order": "desc"
        }
        
        response = client.get("/api/v1/files", headers=auth_headers, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 10
    
    def test_list_files_invalid_pagination(self, client: TestClient, auth_headers):
        """Test listing files with invalid pagination"""
        params = {
            "page": 0,  # Invalid page
            "limit": 200  # Exceeds maximum
        }
        
        response = client.get("/api/v1/files", headers=auth_headers, params=params)
        assert response.status_code == 422  # Validation error
    
    def test_get_file_metadata_success(self, client: TestClient, auth_headers):
        """Test getting file metadata"""
        # First upload a file
        files = {
            "file": ("test.enc", BytesIO(b"test content"), "application/octet-stream")
        }
        
        data = {
            "encrypted_filename": "encrypted_filename_base64",
            "encrypted_metadata": json.dumps({"encrypted_size": "test"}),
            "file_size": 12
        }
        
        upload_response = client.post(
            "/api/v1/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        file_id = upload_response.json()["data"]["file_id"]
        
        # Get metadata
        response = client.get(f"/api/v1/files/{file_id}", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["id"] == file_id
    
    def test_get_file_metadata_not_found(self, client: TestClient, auth_headers):
        """Test getting metadata for non-existent file"""
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/v1/files/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404  # Not found
    
    def test_download_file_success(self, client: TestClient, auth_headers):
        """Test file download URL generation"""
        # First upload a file
        files = {
            "file": ("test.enc", BytesIO(b"download test"), "application/octet-stream")
        }
        
        data = {
            "encrypted_filename": "encrypted_filename_base64",
            "encrypted_metadata": json.dumps({"encrypted_size": "test"}),
            "file_size": 13
        }
        
        upload_response = client.post(
            "/api/v1/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        file_id = upload_response.json()["data"]["file_id"]
        
        # Get download URL
        response = client.get(f"/api/v1/files/{file_id}/download", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "download_url" in result["data"]
        assert "expires_in" in result["data"]
    
    def test_delete_file_soft_delete(self, client: TestClient, auth_headers):
        """Test soft delete of file"""
        # First upload a file
        files = {
            "file": ("delete_test.enc", BytesIO(b"delete me"), "application/octet-stream")
        }
        
        data = {
            "encrypted_filename": "encrypted_filename_base64",
            "encrypted_metadata": json.dumps({"encrypted_size": "test"}),
            "file_size": 9
        }
        
        upload_response = client.post(
            "/api/v1/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        file_id = upload_response.json()["data"]["file_id"]
        
        # Delete file
        response = client.delete(f"/api/v1/files/{file_id}", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "deleted_at" in result["data"]
    
    def test_delete_file_permanent(self, client: TestClient, auth_headers):
        """Test permanent delete of file"""
        # First upload a file
        files = {
            "file": ("perm_delete.enc", BytesIO(b"delete permanently"), "application/octet-stream")
        }
        
        data = {
            "encrypted_filename": "encrypted_filename_base64", 
            "encrypted_metadata": json.dumps({"encrypted_size": "test"}),
            "file_size": 17
        }
        
        upload_response = client.post(
            "/api/v1/files/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        file_id = upload_response.json()["data"]["file_id"]
        
        # Permanently delete file
        response = client.delete(f"/api/v1/files/{file_id}/permanent", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True