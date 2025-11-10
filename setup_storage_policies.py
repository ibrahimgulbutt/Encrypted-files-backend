#!/usr/bin/env python3
"""
Supabase Storage RLS Policy Setup Script
Run this in Supabase SQL Editor to set up proper storage policies
"""

RLS_POLICIES = """
-- Enable RLS on storage.objects if not already enabled
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Enable upload for authenticated users" ON storage.objects;
DROP POLICY IF EXISTS "Enable read for own files" ON storage.objects;
DROP POLICY IF EXISTS "Enable delete for own files" ON storage.objects;
DROP POLICY IF EXISTS "Enable update for own files" ON storage.objects;

-- Policy 1: Allow authenticated users to upload files to their own folder
CREATE POLICY "Enable upload for authenticated users" ON storage.objects
FOR INSERT 
WITH CHECK (
  auth.role() = 'authenticated' 
  AND bucket_id = 'Files'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 2: Allow users to read their own files
CREATE POLICY "Enable read for own files" ON storage.objects
FOR SELECT 
USING (
  auth.role() = 'authenticated' 
  AND bucket_id = 'Files'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 3: Allow users to delete their own files
CREATE POLICY "Enable delete for own files" ON storage.objects
FOR DELETE 
USING (
  auth.role() = 'authenticated' 
  AND bucket_id = 'Files'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 4: Allow users to update their own files
CREATE POLICY "Enable update for own files" ON storage.objects
FOR UPDATE 
USING (
  auth.role() = 'authenticated' 
  AND bucket_id = 'Files'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON storage.objects TO authenticated;
GRANT SELECT ON storage.buckets TO authenticated;

-- Ensure the Files bucket exists and is properly configured
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('Files', 'Files', false, 52428800, null) -- 50MB limit
ON CONFLICT (id) DO UPDATE SET 
  file_size_limit = 52428800,
  public = false;
"""

ALTERNATIVE_PUBLIC_BUCKET = """
-- ALTERNATIVE: Make bucket public (for development/testing only)
-- WARNING: This allows anyone to read files if they know the URL

UPDATE storage.buckets 
SET public = true 
WHERE id = 'Files';

-- Simple policy for public bucket
DROP POLICY IF EXISTS "Public bucket access" ON storage.objects;
CREATE POLICY "Public bucket access" ON storage.objects
FOR ALL 
USING (bucket_id = 'Files');
"""

if __name__ == "__main__":
    print("🔐 Supabase Storage RLS Policy Setup")
    print("=" * 50)
    print()
    print("📋 Copy and paste these SQL commands into your Supabase SQL Editor:")
    print("   1. Go to: https://supabase.com/dashboard/project/[your-project]/sql")
    print("   2. Create a new query")
    print("   3. Paste the SQL below and click 'Run'")
    print()
    print("🔒 SECURE OPTION (Recommended for Production):")
    print("-" * 50)
    print(RLS_POLICIES)
    print()
    print("🌐 SIMPLE OPTION (Development/Testing Only):")
    print("-" * 50)
    print(ALTERNATIVE_PUBLIC_BUCKET)
    print()
    print("⚠️  IMPORTANT NOTES:")
    print("   • The secure option requires JWT authentication")
    print("   • Files are stored in user-specific folders: user_id/file_id.enc")
    print("   • The public option is ONLY for development/testing")
    print("   • After running, test file upload again")