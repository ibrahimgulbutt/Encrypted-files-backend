#!/usr/bin/env python3
"""
Storage Diagnostic Script
Helps identify storage quota and Supabase bucket issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_supabase
from services.user_service import UserService
from config.settings import settings
import asyncio

async def diagnose_storage():
    """Diagnose storage issues"""
    print("🔍 Storage Diagnostic Report")
    print("=" * 50)
    
    # Initialize services
    supabase = get_supabase()
    user_service = UserService(supabase)
    
    print(f"📊 Configuration Settings:")
    print(f"   • Storage Bucket: {settings.storage_bucket_name}")
    print(f"   • Max File Size: {settings.max_file_size_mb} MB")
    print(f"   • Default Storage Limit: {settings.default_storage_limit_gb} GB")
    print(f"   • Default Storage Limit (bytes): {settings.default_storage_limit_bytes:,}")
    print()
    
    # Test Supabase connection
    try:
        print("🔗 Testing Supabase Connection...")
        users = supabase.table("users").select("id, email, storage_used, storage_limit").limit(5).execute()
        print(f"   ✅ Connection successful - Found {len(users.data)} users")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Check bucket exists
    try:
        print(f"\n📦 Testing Storage Bucket '{settings.storage_bucket_name}'...")
        bucket_files = supabase.storage.from_(settings.storage_bucket_name).list()
        print(f"   ✅ Bucket accessible - Found {len(bucket_files)} items")
    except Exception as e:
        print(f"   ❌ Bucket access failed: {e}")
        print(f"   💡 Solution: Create bucket '{settings.storage_bucket_name}' in Supabase dashboard")
        return
    
    # Check user storage quotas
    print(f"\n👥 User Storage Analysis:")
    try:
        for user_data in users.data[:3]:  # Check first 3 users
            user_id = user_data['id']
            email = user_data['email']
            storage_used = user_data['storage_used']
            storage_limit = user_data['storage_limit']
            
            print(f"   User: {email}")
            print(f"      • Used: {storage_used:,} bytes ({storage_used/1024/1024:.2f} MB)")
            print(f"      • Limit: {storage_limit:,} bytes ({storage_limit/1024/1024/1024:.2f} GB)")
            print(f"      • Available: {storage_limit - storage_used:,} bytes")
            print(f"      • Usage: {(storage_used/storage_limit*100):.1f}%")
            
            if storage_limit - storage_used <= 0:
                print(f"      ❌ QUOTA EXCEEDED - No space available!")
            else:
                print(f"      ✅ Space available")
            print()
            
    except Exception as e:
        print(f"   ❌ User analysis failed: {e}")
    
    # Test file upload permissions
    try:
        print("🔐 Testing Storage Permissions...")
        test_content = b"test content for permissions"
        test_path = "test_permission_check.txt"
        
        # Try to upload test file
        upload_result = supabase.storage.from_(settings.storage_bucket_name).upload(
            path=test_path,
            file=test_content,
            file_options={"content-type": "text/plain"}
        )
        print(f"   ✅ Upload permission: OK")
        
        # Clean up test file
        supabase.storage.from_(settings.storage_bucket_name).remove([test_path])
        print(f"   ✅ Delete permission: OK")
        
    except Exception as e:
        print(f"   ❌ Storage permission error: {e}")
        print(f"   💡 Solution: Check bucket policies in Supabase dashboard")
    
    print("\n🔧 Recommended Solutions:")
    print("   1. Check Supabase dashboard for:")
    print(f"      • Bucket '{settings.storage_bucket_name}' exists")
    print("      • Bucket is public or has proper RLS policies")
    print("      • Storage quotas in Supabase account")
    print("   2. Reset user storage quotas if needed")
    print("   3. Check database constraints on storage fields")

if __name__ == "__main__":
    asyncio.run(diagnose_storage())