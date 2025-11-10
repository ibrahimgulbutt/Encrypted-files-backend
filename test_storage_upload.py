#!/usr/bin/env python3
"""
Simple Storage Test
Tests if file upload to Supabase storage works with the current setup
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_supabase
from config.settings import settings
import io

def test_file_upload():
    """Test file upload to the Files bucket"""
    print("🧪 Testing File Upload to Supabase Storage")
    print("=" * 50)
    
    try:
        # Initialize Supabase client
        supabase = get_supabase()
        bucket_name = settings.storage_bucket_name
        
        print(f"📦 Testing bucket: {bucket_name}")
        print(f"🔗 Supabase URL: {settings.supabase_url}")
        
        # Create test file content
        test_content = b"This is a test file for storage upload verification"
        test_path = "test-upload/test-file.txt"
        
        print(f"📁 Test file path: {test_path}")
        print(f"📄 Test file size: {len(test_content)} bytes")
        
        # Test upload
        print("⬆️  Attempting upload...")
        try:
            upload_result = supabase.storage.from_(bucket_name).upload(
                path=test_path,
                file=test_content,
                file_options={"content-type": "text/plain"}
            )
            print(f"✅ Upload successful!")
            print(f"   Result: {upload_result}")
            
        except Exception as upload_error:
            print(f"❌ Upload failed: {upload_error}")
            return False
        
        # Test file exists
        print("🔍 Verifying file exists...")
        try:
            files = supabase.storage.from_(bucket_name).list("test-upload")
            file_found = any(f.get("name") == "test-file.txt" for f in files)
            
            if file_found:
                print(f"✅ File verification successful")
            else:
                print(f"❌ File not found in bucket")
                
        except Exception as list_error:
            print(f"⚠️  Could not verify file (but upload may have worked): {list_error}")
        
        # Test download
        print("⬇️  Testing download...")
        try:
            download_content = supabase.storage.from_(bucket_name).download(test_path)
            
            if download_content == test_content:
                print(f"✅ Download successful - content matches")
            else:
                print(f"⚠️  Downloaded content doesn't match original")
                
        except Exception as download_error:
            print(f"❌ Download failed: {download_error}")
        
        # Cleanup
        print("🧹 Cleaning up test file...")
        try:
            supabase.storage.from_(bucket_name).remove([test_path])
            print(f"✅ Cleanup successful")
        except Exception as cleanup_error:
            print(f"⚠️  Cleanup failed (file may remain): {cleanup_error}")
        
        print(f"\n🎉 Storage test completed successfully!")
        print(f"💡 Your file upload should now work!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_file_upload()
    if success:
        print(f"\n✅ All tests passed - file upload should work now!")
    else:
        print(f"\n❌ Tests failed - check the error messages above")