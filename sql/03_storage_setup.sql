-- Create storage bucket (Run this in Supabase SQL Editor or via Dashboard)
-- Note: This assumes you have the necessary permissions

-- 1. First, create the bucket using Supabase client or dashboard:
-- Storage > Create Bucket > Name: "encrypted-files" > Public: false

-- 2. Or create via SQL (if permissions allow):
INSERT INTO storage.buckets (id, name, public)
VALUES ('Files', 'Files', false)
ON CONFLICT (id) DO NOTHING;

-- 3. Storage policies for the Files bucket
-- These need to be created in Supabase Dashboard > Storage > Files > Policies

-- Policy: "Users can upload their own files"
CREATE POLICY "Users can upload their own files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'Files' 
        AND auth.role() = 'authenticated'
        AND (storage.foldername(name))[1] = auth.uid()::text
    );

-- Policy: "Users can view their own files"  
CREATE POLICY "Users can view their own files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'Files'
        AND auth.role() = 'authenticated' 
        AND (storage.foldername(name))[1] = auth.uid()::text
    );

-- Policy: "Users can update their own files"
CREATE POLICY "Users can update their own files" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'Files'
        AND auth.role() = 'authenticated'
        AND (storage.foldername(name))[1] = auth.uid()::text
    );

-- Policy: "Users can delete their own files"
CREATE POLICY "Users can delete their own files" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'Files'
        AND auth.role() = 'authenticated'
        AND (storage.foldername(name))[1] = auth.uid()::text
    );

-- Enable RLS on storage.objects (should already be enabled)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;