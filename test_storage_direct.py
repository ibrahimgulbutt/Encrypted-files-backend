#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_supabase
from config.storage import StorageService
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def test_storage_upload():
    """Test storage upload directly"""
    
    try:
        # Get Supabase service client (with admin privileges)
        from config.database import get_supabase_service
        client = get_supabase_service()
        print("✅ Supabase service client created")
        
        # Create storage service
        storage = StorageService(client)
        print("✅ Storage service created")
        
        # Create a test file
        test_content = b"This is a test file for storage upload"
        test_file = BytesIO(test_content)
        
        # Test upload
        print("📤 Testing file upload...")
        
        result = storage.client.storage.from_("Files").upload(
            path="test/test-file.txt",
            file=test_content,
            file_options={"content-type": "text/plain"}
        )
        
        print(f"✅ Upload successful: {result}")
        
        # Test cleanup - delete the test file
        try:
            delete_result = storage.client.storage.from_("Files").remove(["test/test-file.txt"])
            print(f"🗑️ Cleanup successful: {delete_result}")
        except Exception as e:
            print(f"⚠️ Cleanup failed (not critical): {e}")
            
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_storage_upload()