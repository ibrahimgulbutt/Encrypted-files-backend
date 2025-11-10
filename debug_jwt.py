#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_supabase_authenticated
from utils.jwt import JWTManager
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def test_authenticated_client():
    """Test creating authenticated Supabase client"""
    
    # Test with a sample JWT token format
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"  # Sample JWT format
    
    print(f"Testing with token: {test_token}")
    print(f"Token type: {type(test_token)}")
    
    try:
        client = get_supabase_authenticated(test_token)
        print("✅ Authenticated client created successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to create authenticated client: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_authenticated_client()