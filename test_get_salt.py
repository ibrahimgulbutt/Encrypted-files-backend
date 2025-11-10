#!/usr/bin/env python3
import requests
import json

def test_get_salt():
    """Test the get-salt endpoint"""
    
    # Use the email from our successful registration
    test_email = "testuser2@example.com"
    
    print("Testing /auth/get-salt endpoint...")
    print(f"Email: {test_email}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/get-salt",
            json={"email": test_email},
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'salt' in data.get('data', {}):
                salt = data['data']['salt']
                print(f"✅ Salt retrieved successfully!")
                print(f"✅ Salt length: {len(salt)} characters")
                print(f"✅ Salt: {salt[:10]}...{salt[-10:]} (truncated)")
            else:
                print("❌ Invalid response format")
        elif response.status_code == 404:
            print("❌ User not found")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing get-salt: {e}")

def test_nonexistent_user():
    """Test get-salt with non-existent user"""
    
    print("\n" + "="*50)
    print("Testing with non-existent user...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/get-salt",
            json={"email": "nonexistent@example.com"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404:
            print("✅ Correctly returns 404 for non-existent user")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing non-existent user: {e}")

if __name__ == "__main__":
    test_get_salt()
    test_nonexistent_user()