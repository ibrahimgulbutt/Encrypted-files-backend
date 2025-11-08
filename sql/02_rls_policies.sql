-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- Users table RLS policies
-- Users can only see and modify their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- For user registration (handled by service role)
CREATE POLICY "Allow user registration" ON users
    FOR INSERT WITH CHECK (true);

-- Files table RLS policies
-- Users can only see their own files
CREATE POLICY "Users can view own files" ON files
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- Users can insert their own files
CREATE POLICY "Users can insert own files" ON files
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- Users can update their own files
CREATE POLICY "Users can update own files" ON files
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Users can delete their own files
CREATE POLICY "Users can delete own files" ON files
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Storage bucket policies (to be applied in Supabase dashboard)
-- These need to be created in the Supabase dashboard under Storage > Policies

/*
Bucket: encrypted-files

Policy 1: "Users can upload their own files"
- Policy type: INSERT
- Target roles: authenticated
- USING expression: 
  bucket_id = 'encrypted-files' AND 
  (storage.foldername(name))[1] = auth.uid()::text

Policy 2: "Users can view their own files"
- Policy type: SELECT  
- Target roles: authenticated
- USING expression:
  bucket_id = 'encrypted-files' AND 
  (storage.foldername(name))[1] = auth.uid()::text

Policy 3: "Users can update their own files"
- Policy type: UPDATE
- Target roles: authenticated
- USING expression:
  bucket_id = 'encrypted-files' AND 
  (storage.foldername(name))[1] = auth.uid()::text

Policy 4: "Users can delete their own files"
- Policy type: DELETE
- Target roles: authenticated
- USING expression:
  bucket_id = 'encrypted-files' AND 
  (storage.foldername(name))[1] = auth.uid()::text
*/

-- Create a function to check storage quota before file upload
CREATE OR REPLACE FUNCTION check_storage_quota(user_uuid UUID, file_size_bytes BIGINT)
RETURNS BOOLEAN AS $$
DECLARE
    current_usage BIGINT;
    storage_limit BIGINT;
BEGIN
    SELECT storage_used, users.storage_limit 
    INTO current_usage, storage_limit
    FROM users 
    WHERE id = user_uuid;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    RETURN (current_usage + file_size_bytes) <= storage_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to get user storage stats
CREATE OR REPLACE FUNCTION get_user_storage_stats(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'storage_used', u.storage_used,
        'storage_limit', u.storage_limit,
        'storage_available', (u.storage_limit - u.storage_used),
        'storage_percentage', ROUND((u.storage_used::DECIMAL / u.storage_limit::DECIMAL) * 100, 2),
        'file_count', COALESCE(file_stats.file_count, 0),
        'largest_file_size', COALESCE(file_stats.largest_file_size, 0)
    )
    INTO result
    FROM users u
    LEFT JOIN (
        SELECT 
            user_id,
            COUNT(*) as file_count,
            MAX(file_size) as largest_file_size
        FROM files 
        WHERE is_deleted = false 
        GROUP BY user_id
    ) file_stats ON u.id = file_stats.user_id
    WHERE u.id = user_uuid;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;