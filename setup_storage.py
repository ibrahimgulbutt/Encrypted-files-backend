"""
Supabase Storage Setup Script
This script helps configure the storage bucket for the encrypted file storage system
"""

from config.database import get_supabase
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

def setup_storage_bucket():
    """Set up the storage bucket and permissions"""
    print("🔧 Setting up Supabase Storage...")
    
    try:
        # Use regular client since bucket is public
        supabase = get_supabase()
        bucket_name = settings.storage_bucket_name
        
        print(f"📦 Configuring bucket: {bucket_name}")
        
        # Check if bucket exists
        try:
            buckets = supabase.storage.list_buckets()
            bucket_exists = any(bucket.name == bucket_name for bucket in buckets)
            
            if bucket_exists:
                print(f"   ✅ Bucket '{bucket_name}' already exists")
            else:
                print(f"   ❌ Bucket '{bucket_name}' does not exist")
                print(f"   💡 Please create bucket '{bucket_name}' in Supabase dashboard")
                return False
                
        except Exception as e:
            print(f"   ❌ Error checking buckets: {e}")
            return False
        
        # Test upload permission
        test_content = b"test file content"
        test_path = "test/permission_check.txt"
        
        try:
            # Try to upload test file
            upload_result = supabase.storage.from_(bucket_name).upload(
                path=test_path,
                file=test_content,
                file_options={"content-type": "text/plain"}
            )
            print(f"   ✅ Upload test successful")
            
            # Clean up test file
            supabase.storage.from_(bucket_name).remove([test_path])
            print(f"   ✅ Delete test successful")
            
        except Exception as e:
            print(f"   ❌ Permission error: {e}")
            print(f"   💡 Make bucket public or set up RLS policies")
            return False
            
        print(f"🎉 Storage setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_storage_bucket()