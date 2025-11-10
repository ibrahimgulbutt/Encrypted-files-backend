#!/usr/bin/env python3
"""
Authenticated Storage Test
Tests file upload with a real user account to work with RLS policies
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import hashlib
import base64
import json

def test_authenticated_upload():
    """Test file upload with authentication"""
    print("🔐 Testing Authenticated File Upload")
    print("=" * 50)
    
    # User credentials
    email = "ibrahimgulbutt242@gmail.com"
    password = "Qwe12345678!"
    
    # Server URL
    base_url = "http://localhost:8000/api/v1"
    
    try:
        # Step 1: Get user salt
        print("🧂 Step 1: Getting user salt...")
        salt_response = requests.post(
            f"{base_url}/auth/get-salt",
            json={"email": email},
            timeout=10
        )
        
        if salt_response.status_code != 200:
            print(f"❌ Failed to get salt: {salt_response.status_code} - {salt_response.text}")
            return False
            
        salt_data = salt_response.json()
        user_salt = salt_data["data"]["salt"]
        print(f"✅ Got user salt: {user_salt[:8]}...")
        
        # Step 2: Hash password client-side
        print("🔐 Step 2: Hashing password...")
        password_hash = hashlib.sha256(password.encode()).digest()
        password_hash_b64 = base64.b64encode(password_hash).decode('utf-8')
        print(f"✅ Password hashed: {password_hash_b64[:8]}...")
        
        # Step 3: Login
        print("🚪 Step 3: Logging in...")
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={
                "email": email,
                "password_hash": password_hash_b64
            },
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
            
        login_data = login_response.json()
        access_token = login_data["data"]["access_token"]
        print(f"✅ Login successful: {access_token[:20]}...")
        
        # Step 4: Prepare file upload
        print("📁 Step 4: Preparing file upload...")
        
        # Create test file content
        test_file_content = b"This is a test encrypted file content for storage verification"
        
        # Simulate client-side encryption metadata
        file_metadata = {
            "original_name": "test-file.txt",
            "original_size": len(test_file_content),
            "content_type": "text/plain",
            "encryption_iv": base64.b64encode(b"dummy_iv_123456").decode(),
            "checksum": hashlib.sha256(test_file_content).hexdigest()
        }
        
        # Prepare form data
        files = {
            'file': ('encrypted_file.enc', test_file_content, 'application/octet-stream')
        }
        
        data = {
            'encrypted_filename': base64.b64encode(b"test-file.txt").decode(),
            'encrypted_metadata': json.dumps(file_metadata),
            'file_size': len(test_file_content)
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        print(f"📄 File size: {len(test_file_content)} bytes")
        print(f"🔐 Encrypted filename: {data['encrypted_filename']}")
        
        # Step 5: Upload file
        print("⬆️  Step 5: Uploading file...")
        upload_response = requests.post(
            f"{base_url}/files/upload",
            files=files,
            data=data,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Upload response status: {upload_response.status_code}")
        print(f"📊 Upload response: {upload_response.text}")
        
        if upload_response.status_code == 201:
            print("🎉 File upload successful!")
            upload_data = upload_response.json()
            file_id = upload_data.get("data", {}).get("id")
            print(f"📁 File ID: {file_id}")
            return True
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_authenticated_upload()
    if success:
        print(f"\n✅ Authenticated upload test passed!")
        print(f"🎯 Your file upload system is working correctly!")
    else:
        print(f"\n❌ Test failed - check the error messages above")