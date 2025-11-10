#!/usr/bin/env python3
import requests
import json
import base64
import hashlib

# Test data that matches frontend format
email = "testuser2@example.com"
password = "testpassword123"

# Simulate frontend password hashing
salt_bytes = b"1234567890123456"  # 16 bytes
salt_b64 = base64.b64encode(salt_bytes).decode('utf-8')  # 24 chars

password_hash = hashlib.sha256(password.encode()).digest()
password_hash_b64 = base64.b64encode(password_hash).decode('utf-8')  # 43 chars

print(f"Salt length: {len(salt_b64)} characters")
print(f"Password hash length: {len(password_hash_b64)} characters")
print(f"Total concatenated length: {len(password_hash_b64 + salt_b64)} characters")

# Test registration
registration_data = {
    "email": email,
    "password_hash": password_hash_b64,
    "salt": salt_b64
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/auth/register",
        json=registration_data,
        timeout=10
    )
    
    print(f"\nRegistration Response Status: {response.status_code}")
    print(f"Registration Response: {response.text}")
    
    if response.status_code == 201:
        print("✅ Registration successful - PBKDF2 hashing fix working!")
        response_data = response.json()
        print(f"✅ User ID: {response_data.get('data', {}).get('user_id', 'N/A')}")
    elif response.status_code == 200:
        print("✅ Registration successful - backend working!")
    elif response.status_code == 422:
        print("❌ Still getting validation error")
    else:
        print(f"❓ Unexpected response: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error testing registration: {e}")